#!/bin/bash
# Build output logger and splitter for REG-Linux
#
# Reads Buildroot output from stdin and:
#   1. Writes full output to <output-dir>/build/full-build.log
#   2. Splits per-package output into <output-dir>/build/logs/<package>.log
#   3. Displays [REG-PROGRESS] lines on the console in real-time
#   4. On build failure: dumps full log of each failed package to stdout
#
# Usage:
#   <docker build command> 2>&1 | build-logger.sh <output-dir>

OUTPUT_BASE="$1"

if [ -z "$OUTPUT_BASE" ]; then
    echo "Usage: $0 <output-dir>" >&2
    exit 1
fi

BUILD_DIR="$OUTPUT_BASE/build"
LOG_DIR="$BUILD_DIR/logs"
FULL_LOG="$BUILD_DIR/full-build.log"
ERRORS_FILE="$BUILD_DIR/build-errors.log"

mkdir -p "$LOG_DIR"

# Clean previous run
> "$FULL_LOG"
> "$ERRORS_FILE"

# Reset progress state (counter, start time, active packages)
# so incremental rebuilds don't carry over stale values
rm -rf "$BUILD_DIR/.build-progress"

# Record build start timestamp for filtering build-time.log later
BUILD_START_TS=$(date +%s)

# Track current package for log splitting
current_pkg=""
current_pkg_log=""
# Once packages are done, Buildroot runs post-build/post-image scripts,
# filesystem generation, etc. Switch to passthrough mode for those.
passthrough=0

# Track last step per package (for failure reporting)
declare -A pkg_last_step

SEPARATOR="======================================================================"

# Process all lines from stdin
while IFS= read -r line; do
    # Check for progress lines from instrumentation script — display immediately
    if [[ "$line" == *"[REG-PROGRESS]"* ]]; then
        echo "${line#*\[REG-PROGRESS\] }"
        echo "$line" >> "$FULL_LOG"
        continue
    fi

    # Write every line to full log
    echo "$line" >> "$FULL_LOG"

    # In passthrough mode (post-build phase), echo everything to console
    if [ "$passthrough" -eq 1 ]; then
        echo "$line"
        # Still detect errors (locale-independent: *** is universal)
        if [[ "$line" == *"*** ["*"]"* ]]; then
            if ! grep -q "^post-build|" "$ERRORS_FILE" 2>/dev/null; then
                echo "post-build|post-build|$(date +%s)|(see full log)" >> "$ERRORS_FILE"
            fi
        fi
        continue
    fi

    # Strip ANSI codes for marker detection
    clean_line=$(printf '%s' "$line" | sed 's/\x1b\[[0-9;]*m//g')

    # Detect post-build phase: >>> markers that aren't package steps
    # Package markers: ">>> <pkg> <version> <step>" (pkg is lowercase)
    # Post-build markers: ">>>   Finalizing ...", ">>>   Executing ...", etc.
    # (extra spaces because PKG_NAME and PKG_VERSION are empty)
    if [[ "$clean_line" =~ ^'>>>'[[:space:]]+[A-Z] ]]; then
        passthrough=1
        echo "$line"
        continue
    fi

    # Detect Buildroot >>> markers: ">>> <package> <version> <step>"
    if [[ "$clean_line" =~ ^'>>> '([^ ]+)' '([^ ]+)' '(.+)$ ]]; then
        pkg="${BASH_REMATCH[1]}"
        step="${BASH_REMATCH[3]}"

        current_pkg="$pkg"
        current_pkg_log="$LOG_DIR/$pkg.log"
        pkg_last_step[$pkg]="$step"

        # Write step header to per-package log
        {
            echo ""
            echo "--- $step ---"
            echo "$line"
        } >> "$current_pkg_log"
        continue
    fi

    # Append to current package log if we have one
    if [ -n "$current_pkg_log" ]; then
        echo "$line" >> "$current_pkg_log"
    fi

    # Detect make errors — use locale-independent pattern: "*** [" is universal
    if [[ "$clean_line" == *"make"*"*** ["*"]"* ]]; then
        # Extract the actual failing package from the stamp file path in the
        # error line, e.g.: .../build/sdl2-2.32.10/.stamp_patched
        # This is more reliable than current_pkg which may be a parallel package.
        failed_pkg=""
        if [[ "$clean_line" =~ /build/([^/]+)/\.stamp_([^][:space:]]+) ]]; then
            dir="${BASH_REMATCH[1]}"
            stamp="${BASH_REMATCH[2]}"
            # Strip version: remove trailing -<digit>... (e.g. sdl2-2.32.10 -> sdl2)
            failed_pkg=$(echo "$dir" | sed 's/-[0-9][^-]*$//')
            failed_step="$stamp"
        fi
        # Fall back to current_pkg if stamp path not in error line
        failed_pkg="${failed_pkg:-$current_pkg}"
        failed_step="${failed_step:-${pkg_last_step[$current_pkg]:-unknown}}"

        if [ -n "$failed_pkg" ]; then
            if ! grep -q "^${failed_pkg}|" "$ERRORS_FILE" 2>/dev/null; then
                # Store: pkg|step|timestamp|builddir (builddir used for log extraction)
                echo "${failed_pkg}|${failed_step}|$(date +%s)|${dir:-unknown}" >> "$ERRORS_FILE"
            fi
        fi
    fi
done

# Fallback: if no errors detected via make output, check build-time.log
# for packages that started a step but never finished (indicates failure).
# ONLY look at entries from the CURRENT build (after BUILD_START_TS).
if [ ! -s "$ERRORS_FILE" ]; then
    if [ -f "$BUILD_DIR/build-time.log" ]; then
        declare -A started_pkgs
        while IFS=: read -r ts phase step pkg; do
            # Only consider entries from this build
            ts_int="${ts%%.*}"
            [ "$ts_int" -lt "$BUILD_START_TS" ] 2>/dev/null && continue

            pkg="${pkg// /}"
            step="${step// /}"
            phase="${phase// /}"
            if [ "$phase" = "start" ]; then
                started_pkgs["$pkg:$step"]=1
            elif [ "$phase" = "end" ]; then
                unset 'started_pkgs[$pkg:$step]' 2>/dev/null || true
            fi
        done < "$BUILD_DIR/build-time.log"

        for key in "${!started_pkgs[@]}"; do
            pkg="${key%%:*}"
            step="${key##*:}"
            echo "${pkg}|${step}|$(date +%s)|unknown" >> "$ERRORS_FILE"
        done
    fi
fi

# Dump failed package logs
if [ -s "$ERRORS_FILE" ]; then
    echo ""
    echo "$SEPARATOR"
    echo " BUILD FAILED — Full logs of failed package(s) below"
    echo "$SEPARATOR"

    while IFS='|' read -r pkg step _timestamp builddir; do
        echo ""
        echo "$SEPARATOR"
        echo " FAILED: $pkg at step: $step"
        echo "$SEPARATOR"
        echo ""

        # Extract relevant output from full-build.log.
        # With parallel builds, per-package logs are polluted with
        # interleaved output, so we filter the full log instead:
        #   - Lines from this package's build/per-package directories
        #   - The >>> markers for this package
        #   - The make error line
        if [ "$builddir" != "unknown" ] && [ -n "$builddir" ]; then
            grep -E \
                "/build/${builddir}/|/per-package/${pkg}/|>>> ${pkg} |\*\*\*.*${builddir}" \
                "$FULL_LOG" 2>/dev/null
        fi

        # Also show the error line with surrounding context (catches
        # compiler/patch errors that don't reference the build dir)
        if [ "$builddir" != "unknown" ] && [ -n "$builddir" ]; then
            echo ""
            echo "--- Error context ---"
            grep -B 30 -A 5 "\*\*\*.*${builddir}" "$FULL_LOG" 2>/dev/null | head -50
        else
            # No builddir: fall back to grepping for the package name
            echo "--- Error context ---"
            grep -B 30 -A 5 "\*\*\*.*${pkg}" "$FULL_LOG" 2>/dev/null | head -50
        fi

        echo ""
        echo "$SEPARATOR"
        echo " END OF LOG: $pkg"
        echo "$SEPARATOR"
    done < "$ERRORS_FILE"

    # Summary
    fail_count=$(wc -l < "$ERRORS_FILE")
    echo ""
    echo "$SEPARATOR"
    echo " SUMMARY: $fail_count package(s) failed:"
    while IFS='|' read -r pkg step _timestamp builddir; do
        echo "   - $pkg (step: $step)"
    done < "$ERRORS_FILE"
    echo ""
    echo " Full build log: $FULL_LOG"
    echo "$SEPARATOR"
    exit 1

else
    # Check if full log contains any make error indicators we might have missed
    # Use locale-independent pattern: "*** [" is always present
    if grep -q '\*\*\* \[' "$FULL_LOG" 2>/dev/null; then
        echo ""
        echo "$SEPARATOR"
        echo " BUILD FAILED — could not identify specific package"
        echo " Check full log: $FULL_LOG"
        echo ""
        echo " Error lines found:"
        grep '\*\*\* \[' "$FULL_LOG" | tail -20
        echo "$SEPARATOR"
        exit 1
    fi

    # Success
    echo ""
    echo "$SEPARATOR"
    echo " BUILD SUCCESSFUL"
    if [ -f "$BUILD_DIR/.build-progress/start_time" ]; then
        start_time=$(cat "$BUILD_DIR/.build-progress/start_time")
        now=$(date +%s)
        elapsed=$((now - start_time))
        hours=$((elapsed / 3600))
        mins=$(( (elapsed % 3600) / 60))
        secs=$((elapsed % 60))
        printf " Total build time: %dh%02dm%02ds\n" "$hours" "$mins" "$secs"
    fi
    echo " Full build log: $FULL_LOG"
    echo "$SEPARATOR"
    exit 0
fi
