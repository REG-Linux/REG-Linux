#!/bin/bash
# Build instrumentation script for Buildroot
# Used via BR2_INSTRUMENTATION_SCRIPTS to track build progress.
#
# Called by Buildroot at each step with:
#   $1 = "start" or "end"
#   $2 = step name (download, extract, patch, configure, build, install-*)
#   $3 = package name
#
# Env (set by Makefile):
#   REG_BUILD_TOTAL  — total number of packages (estimated)
#   BUILD_DIR        — Buildroot build directory (set by Buildroot)
#
# Outputs [REG-PROGRESS] prefixed lines to stderr (flows through pipe
# to build-logger.sh which displays them on the console in real-time).

PHASE="$1"    # start / end
STEP="$2"     # download, extract, patch, configure, build, install-*
PACKAGE="$3"  # package name

# Determine build directory
# REG_BUILD_DIR is passed explicitly by the Makefile via Docker -e.
# BUILD_DIR and O are make variables that Buildroot does NOT export
# (O is explicitly unexported), so they won't be in the environment.
BUILD_DIR="${REG_BUILD_DIR:-${BUILD_DIR:-${O:+$O/build}}}"
[ -z "$BUILD_DIR" ] && exit 0

STATUS_DIR="$BUILD_DIR/.build-progress"
mkdir -p "$STATUS_DIR"

COUNTER_FILE="$STATUS_DIR/completed_count"
START_TIME_FILE="$STATUS_DIR/start_time"
ACTIVE_DIR="$STATUS_DIR/active"

mkdir -p "$ACTIVE_DIR"

# Record build start time on first invocation
# (build-logger.sh clears .build-progress/ at start, so this
# creates a fresh timestamp for each build)
if [ ! -f "$START_TIME_FILE" ]; then
    date +%s > "$START_TIME_FILE"
fi

TOTAL="${REG_BUILD_TOTAL:-?}"

format_elapsed() {
    local secs="$1"
    if [ "$secs" -ge 3600 ]; then
        printf "%dh%02dm" $((secs / 3600)) $(((secs % 3600) / 60))
    else
        printf "%dm%02ds" $((secs / 60)) $((secs % 60))
    fi
}

format_duration() {
    local secs="$1"
    if [ "$secs" -ge 60 ]; then
        printf "%dm%02ds" $((secs / 60)) $((secs % 60))
    else
        printf "%ds" "$secs"
    fi
}

get_elapsed() {
    local start_time
    start_time=$(cat "$START_TIME_FILE" 2>/dev/null || echo 0)
    local now
    now=$(date +%s)
    echo $((now - start_time))
}

get_completed() {
    cat "$COUNTER_FILE" 2>/dev/null || echo 0
}

# Atomic increment using flock
increment_counter() {
    local file="$1"
    (
        flock -x 200
        local val
        val=$(cat "$file" 2>/dev/null || echo 0)
        echo $((val + 1)) > "$file"
        echo $((val + 1))
    ) 200>"$file.lock"
}

completed=$(get_completed)
elapsed=$(format_elapsed "$(get_elapsed)")

if [ "$PHASE" = "start" ]; then
    # Track this package as active with step and start timestamp
    echo "$STEP $(date +%s)" > "$ACTIVE_DIR/$PACKAGE"

    printf "[REG-PROGRESS] [%3s/%-3s %s] >>> %-30s %s\n" \
        "$completed" "$TOTAL" "$elapsed" "$PACKAGE" "$STEP" >&2

elif [ "$PHASE" = "end" ]; then
    # Calculate step duration
    step_start_time=""
    if [ -f "$ACTIVE_DIR/$PACKAGE" ]; then
        step_start_time=$(awk '{print $2}' "$ACTIVE_DIR/$PACKAGE")
    fi

    duration_str=""
    if [ -n "$step_start_time" ]; then
        now=$(date +%s)
        duration=$((now - step_start_time))
        duration_str=$(format_duration "$duration")
    fi

    # Remove from active
    rm -f "$ACTIVE_DIR/$PACKAGE"

    # Count completed on final install steps (one per package)
    case "$STEP" in
        install-target|install-host|install-images)
            completed=$(increment_counter "$COUNTER_FILE")
            ;;
    esac

    printf "[REG-PROGRESS] [%3s/%-3s %s] <<< %-30s %-20s done (%s)\n" \
        "$completed" "$TOTAL" "$elapsed" "$PACKAGE" "$STEP" "$duration_str" >&2
fi
