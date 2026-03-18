#!/bin/bash
# REG-Linux Package Update Checker
# Uses nvchecker to check for new versions of all packages under package/
# Produces a nicely formatted terminal report
#
# Usage:
#   ./check_all_updates.sh [OPTIONS] [DIR_OR_FILE...]
#
# Options:
#   --updates-only    Only show packages with available updates
#   --json            Output machine-readable JSON instead of terminal report
#   --category CAT    Filter to one category (emulators, ports, engines, etc.)
#   --no-commits      Skip commit-based packages (faster, no git fetches)
#   --select PKG,...  Only check these packages (comma-separated names)
#   --update PKG,...  Check and write new versions to .mk files (comma-separated)
#                     Use --update ALL to update every package that has an update
#   --verbose         Show debug info during scanning
#   --help            Show this help
#
# Environment:
#   GITHUB_TOKEN      GitHub API token for higher rate limits (5000/hr vs 60/hr)

set -euo pipefail

_SCRIPT_PATH="$(cd "$(dirname "$0")" && pwd)"
_ROOT="$(cd "$_SCRIPT_PATH/../.." && pwd)"
_OVERRIDES_FILE="$_SCRIPT_PATH/overrides.conf"
_PACKAGES_EXCLUDE="$_SCRIPT_PATH/packages.exclude"
_TOML_OUT="$_SCRIPT_PATH/nvchecker_all.toml"
_STATE_JSON="$_SCRIPT_PATH/all_state.json"
_NEW_JSON="$_SCRIPT_PATH/all_new.json"
_KEYFILE="$_SCRIPT_PATH/keyfile.toml"
_METADATA="$_SCRIPT_PATH/.pkg_metadata.json"

# CLI options
OPT_UPDATES_ONLY=false
OPT_JSON=false
OPT_CATEGORY=""
OPT_NO_COMMITS=false
OPT_VERBOSE=false
OPT_SELECT=""
OPT_UPDATE=""
SCAN_TARGETS=()

# Counters
declare -i count_total=0
declare -i count_checked=0
declare -i count_uptodate=0
declare -i count_updates=0
declare -i count_errors=0
declare -i count_skipped=0
declare -i count_major=0
declare -i count_minor=0
declare -i count_patch=0

# ── Terminal colors & symbols ───────────────────────────────────────

if [[ -t 1 ]]; then
    C_RESET='\033[0m'
    C_BOLD='\033[1m'
    C_DIM='\033[2m'
    C_GREEN='\033[32m'
    C_YELLOW='\033[33m'
    C_RED='\033[31m'
    C_CYAN='\033[36m'
    C_WHITE='\033[37m'
    C_BG_BLUE='\033[44m'
    SYM_OK='✓'
    SYM_UP='↑'
    SYM_ERR='✗'
    SYM_SKIP='○'
else
    C_RESET='' C_BOLD='' C_DIM='' C_GREEN='' C_YELLOW=''
    C_RED='' C_CYAN='' C_WHITE='' C_BG_BLUE=''
    SYM_OK='OK' SYM_UP='UP' SYM_ERR='ERR' SYM_SKIP='--'
fi

# ── Helpers ─────────────────────────────────────────────────────────

die()  { echo -e "${C_RED}Error: $*${C_RESET}" >&2; exit 1; }
info() { [[ "$OPT_VERBOSE" == true ]] && echo -e "${C_DIM}  $*${C_RESET}" >&2 || true; }
warn() { echo -e "${C_YELLOW}  Warning: $*${C_RESET}" >&2; }

parse_args() {
    while [[ $# -gt 0 ]]; do
        case "$1" in
            --updates-only) OPT_UPDATES_ONLY=true ;;
            --json)         OPT_JSON=true ;;
            --category)     shift; OPT_CATEGORY="$1" ;;
            --no-commits)   OPT_NO_COMMITS=true ;;
            --select)       shift; OPT_SELECT="$1" ;;
            --update)       shift; OPT_UPDATE="$1"; OPT_UPDATES_ONLY=true ;;
            --verbose)      OPT_VERBOSE=true ;;
            --help)         head -19 "$0" | tail -17; exit 0 ;;
            *)              SCAN_TARGETS+=("$1") ;;
        esac
        shift
    done
}

# Extract a make variable value from a .mk file
get_mk_var() {
    local file="$1" var="$2"
    local val
    val="$(grep -m1 "^${var}[[:space:]]*=" "$file" 2>/dev/null | sed "s/^${var}[[:space:]]*=[[:space:]]*//" | sed 's/[[:space:]]*$//')" || true
    # Handle line continuations
    if [[ "$val" == '\' ]]; then
        val="$(grep -A1 "^${var}[[:space:]]*=" "$file" | tail -1 | sed 's/^[[:space:]]*//' | sed 's/[[:space:]]*$//')"
    fi
    echo "$val"
}

# Determine category from file path
get_category() {
    local mk_path="$1"
    local rel="${mk_path#$_ROOT/package/}"
    echo "${rel%%/*}"
}

# Get display name for category
category_label() {
    case "$1" in
        emulators)         echo "Emulators" ;;
        ports)             echo "Ports" ;;
        engines)           echo "Engines" ;;
        retroarch)         echo "RetroArch" ;;
        gpu)               echo "GPU / Vulkan" ;;
        system)            echo "System" ;;
        libraries)         echo "Libraries" ;;
        audio)             echo "Audio" ;;
        network)           echo "Network" ;;
        controllers)       echo "Controllers" ;;
        emulationstation)  echo "EmulationStation" ;;
        frontends)         echo "Frontends" ;;
        themes)            echo "Themes" ;;
        bezels)            echo "Bezels" ;;
        fonts)             echo "Fonts" ;;
        firmwares)         echo "Firmwares" ;;
        boot)              echo "Boot" ;;
        batocera)          echo "Batocera Compat" ;;
        games)             echo "Games" ;;
        multimedia)        echo "Multimedia" ;;
        fpga)              echo "FPGA" ;;
        cases)             echo "Cases" ;;
        toolchain)         echo "Toolchain" ;;
        utils)             echo "Utilities" ;;
        *)                 echo "$1" ;;
    esac
}

# Check if package is excluded
is_excluded() {
    [[ -f "$_PACKAGES_EXCLUDE" ]] && grep -qx "$1" "$_PACKAGES_EXCLUDE" 2>/dev/null
}

# Get overrides for a package
get_overrides() {
    [[ -f "$_OVERRIDES_FILE" ]] || return 0
    grep "^${1}\\..*=.*$" "$_OVERRIDES_FILE" 2>/dev/null | cut -d '.' -f2- | sed 's/=/ = /' || true
}

# Check if overrides contain a specific key
has_override() {
    [[ -f "$_OVERRIDES_FILE" ]] && grep -q "^${1}\\.${2}=" "$_OVERRIDES_FILE" 2>/dev/null
}

# Get commit date from a git repo (used for commit-based versions)
get_commit_date() {
    local url="$1" commit="$2"
    local tmpdir
    tmpdir=$(mktemp -d)
    if git -c init.defaultBranch=tmp init --quiet "$tmpdir" 2>/dev/null && \
       git -C "$tmpdir" fetch --quiet --depth=1 --filter=blob:none "$url" "$commit" 2>/dev/null; then
        git -C "$tmpdir" show -s --format=%ci FETCH_HEAD 2>/dev/null | \
            xargs -I{} date -u -d {} +%Y%m%d.%H%M%S 2>/dev/null
    fi
    rm -rf "$tmpdir" 2>/dev/null
}

# Classify version bump severity
classify_bump() {
    local old="$1" new="$2"
    # Strip common prefixes (v, g, etc.)
    local o="${old#[vVgG]}" n="${new#[vVgG]}"

    # If either is a commit hash, it's a commit update
    if [[ "$old" =~ ^[a-f0-9]{40}$ ]] || [[ "$new" =~ ^[a-f0-9]{40}$ ]]; then
        echo "commits"
        return
    fi

    # Try semver comparison
    local o_major o_minor o_patch n_major n_minor n_patch
    if [[ "$o" =~ ^([0-9]+)\.([0-9]+)\.?([0-9]*) ]] && [[ "$n" =~ ^([0-9]+)\.([0-9]+)\.?([0-9]*) ]]; then
        o_major="${BASH_REMATCH[1]}" # from n match
        IFS='.' read -r o_major o_minor o_patch <<< "$(echo "$o" | grep -oE '^[0-9]+\.[0-9]+\.?[0-9]*')"
        IFS='.' read -r n_major n_minor n_patch <<< "$(echo "$n" | grep -oE '^[0-9]+\.[0-9]+\.?[0-9]*')"
        o_patch="${o_patch:-0}"
        n_patch="${n_patch:-0}"

        if [[ "$n_major" != "$o_major" ]]; then
            echo "major"
        elif [[ "$n_minor" != "$o_minor" ]]; then
            echo "minor"
        else
            echo "patch"
        fi
        return
    fi

    echo "patch"
}

# ── TOML generation ─────────────────────────────────────────────────

init_toml() {
    cat > "$_TOML_OUT" << 'EOF'
[__config__]
max_concurrency = 20
EOF

    # Add keyfile if it exists
    if [[ -f "$_KEYFILE" ]]; then
        sed -i '2a keyfile = "keyfile.toml"' "$_TOML_OUT"
    fi

    cat >> "$_TOML_OUT" << EOF
oldver = "$(basename "$_STATE_JSON")"
newver = "$(basename "$_NEW_JSON")"

EOF

    echo '{"version":2,"data":{}}' > "$_STATE_JSON"
    echo '{}' > "$_METADATA"
}

# Add a package to the state JSON
# $1: package name, $2: version
state_add() {
    local tmp
    tmp=$(jq --arg p "$1" --arg v "$2" '.data[$p] = {version: $v}' "$_STATE_JSON")
    echo "$tmp" > "$_STATE_JSON"
}

# Add a package to the state JSON with revision (for git commits)
# $1: package name, $2: version (date), $3: revision (commit hash)
state_add_git() {
    local tmp
    tmp=$(jq --arg p "$1" --arg v "$2" --arg r "$3" \
        '.data[$p] = {version: $v, revision: $r}' "$_STATE_JSON")
    echo "$tmp" > "$_STATE_JSON"
}

# Store metadata about a package (category, mk_file, original version, site)
# $1: pkg_name, $2: category, $3: mk_file, $4: original_version, $5: site_url
meta_add() {
    local tmp
    tmp=$(jq --arg p "$1" --arg cat "$2" --arg mk "$3" --arg ver "$4" --arg site "$5" \
        '.[$p] = {category: $cat, mk_file: $mk, version: $ver, site: $site}' "$_METADATA")
    echo "$tmp" > "$_METADATA"
}

# Generate TOML entry for a GitHub-sourced package
# $1: pkg_name, $2: owner, $3: repo, $4: version_type (version|commit)
toml_github() {
    local pkg="$1" owner="$2" repo="$3" vtype="$4"
    {
        echo "[$pkg]"
        echo "source = \"github\""
        echo "github = \"$owner/$repo\""
        if [[ "$vtype" == "version" ]]; then
            # Check if override specifies a different method
            if ! has_override "$pkg" "use_max_release" && \
               ! has_override "$pkg" "use_latest_tag"; then
                echo 'use_latest_release = "true"'
            fi
        fi
        get_overrides "$pkg"
        echo
    } >> "$_TOML_OUT"
}

# Generate TOML entry for a GitLab-sourced package
# $1: pkg_name, $2: owner, $3: repo, $4: version_type, $5: host (optional)
toml_gitlab() {
    local pkg="$1" owner="$2" repo="$3" vtype="$4" host="${5:-}"
    {
        echo "[$pkg]"
        echo "source = \"gitlab\""
        echo "gitlab = \"$owner/$repo\""
        [[ -n "$host" ]] && echo "host = \"$host\""
        if [[ "$vtype" == "version" ]]; then
            echo 'use_max_tag = "true"'
        else
            echo 'branch = "master"'
        fi
        get_overrides "$pkg"
        echo
    } >> "$_TOML_OUT"
}

# Generate TOML entry for a git-sourced package
# $1: pkg_name, $2: url
toml_git() {
    local pkg="$1" url="$2"
    {
        echo "[$pkg]"
        echo "source = \"git\""
        echo "git = \"$url\""
        get_overrides "$pkg"
        echo
    } >> "$_TOML_OUT"
}

# ── Package parsing ─────────────────────────────────────────────────

parse_package() {
    local mk_file="$1"
    local pkg_name
    pkg_name="$(basename "$mk_file" .mk)"

    local br_name
    br_name="$(echo "${pkg_name^^}" | tr '-' '_')"

    # Filter by --select list
    if [[ -n "$OPT_SELECT" ]]; then
        local in_select=false
        IFS=',' read -ra _sel_pkgs <<< "$OPT_SELECT"
        for _sp in "${_sel_pkgs[@]}"; do
            [[ "$_sp" == "$pkg_name" ]] && { in_select=true; break; }
        done
        if [[ "$in_select" == false ]]; then
            return
        fi
    fi

    # Filter by --update list (unless ALL)
    if [[ -n "$OPT_UPDATE" ]] && [[ "$OPT_UPDATE" != "ALL" ]]; then
        local in_update=false
        IFS=',' read -ra _upd_pkgs <<< "$OPT_UPDATE"
        for _up in "${_upd_pkgs[@]}"; do
            [[ "$_up" == "$pkg_name" ]] && { in_update=true; break; }
        done
        if [[ "$in_update" == false ]]; then
            return
        fi
    fi

    # Skip excluded packages
    if is_excluded "$pkg_name"; then
        info "$pkg_name: excluded"
        count_skipped+=1
        return
    fi

    # Extract key variables
    local pkg_version pkg_site pkg_site_method
    pkg_version="$(get_mk_var "$mk_file" "${br_name}_VERSION")"
    pkg_site="$(get_mk_var "$mk_file" "${br_name}_SITE")"
    pkg_site_method="$(get_mk_var "$mk_file" "${br_name}_SITE_METHOD")"

    # Skip packages without version or site
    if [[ -z "$pkg_version" ]] || [[ -z "$pkg_site" ]]; then
        info "$pkg_name: no version or site, skipping"
        count_skipped+=1
        return
    fi

    # Skip packages with _SOURCE= (empty source = local package)
    local pkg_source
    pkg_source="$(get_mk_var "$mk_file" "${br_name}_SOURCE")"
    if grep -q "^${br_name}_SOURCE[[:space:]]*=$" "$mk_file" 2>/dev/null; then
        info "$pkg_name: local package (empty SOURCE), skipping"
        count_skipped+=1
        return
    fi

    # If version references another package variable, resolve it
    if [[ "$pkg_version" =~ ^\$\(.*_VERSION\)$ ]]; then
        local ref_var
        ref_var="$(echo "$pkg_version" | grep -oE '[A-Z_]+_VERSION')"
        local ref_name="${ref_var%_VERSION}"
        # Search for the source .mk
        local ref_mk
        ref_mk="$(grep -rl "^${ref_name}[[:space:]]*=" "$_ROOT/package/" --include="*.mk" 2>/dev/null | head -1)" || true
        if [[ -n "$ref_mk" ]]; then
            pkg_version="$(get_mk_var "$ref_mk" "$ref_var")"
        else
            info "$pkg_name: can't resolve version ref $ref_var"
            count_skipped+=1
            return
        fi
    fi

    # Skip if version still contains make variables
    if [[ "$pkg_version" == *'$('* ]]; then
        info "$pkg_name: version contains unresolvable variable: $pkg_version"
        count_skipped+=1
        return
    fi

    # Determine version type
    local vtype="version"
    if echo "$pkg_version" | grep -qE '^[a-f0-9]{40}$'; then
        vtype="commit"
        if [[ "$OPT_NO_COMMITS" == true ]]; then
            info "$pkg_name: commit-based, skipping (--no-commits)"
            count_skipped+=1
            return
        fi
    fi

    local category
    category="$(get_category "$mk_file")"

    # Filter by category if requested
    if [[ -n "$OPT_CATEGORY" ]] && [[ "$category" != "$OPT_CATEGORY" ]]; then
        return
    fi

    count_total+=1

    # Determine site URL for metadata
    local display_site=""

    # ── Check if overrides completely replace the source ──
    if has_override "$pkg_name" "source"; then
        info "$pkg_name: fully overridden source"
        # For overridden sources, just add the overrides as a toml section
        {
            echo "[$pkg_name]"
            get_overrides "$pkg_name"
            echo
        } >> "$_TOML_OUT"
        state_add "$pkg_name" "$pkg_version"
        meta_add "$pkg_name" "$category" "$mk_file" "$pkg_version" ""
        count_checked+=1
        return
    fi

    # ── Parse site to determine source type ──

    # Pattern: $(call github,owner,repo,version)
    if [[ "$pkg_site" =~ ^\$\(call\ github, ]]; then
        local owner repo
        owner="$(echo "$pkg_site" | cut -d',' -f2 | sed 's|^[/ ]*||;s|[/ ]*$||')"
        repo="$(echo "$pkg_site" | cut -d',' -f3 | sed 's/[)].*//' | sed 's|^[/ ]*||;s|[/ ]*$||')"
        display_site="https://github.com/$owner/$repo"

        if [[ "$vtype" == "commit" ]]; then
            local cdate
            cdate="$(get_commit_date "$display_site" "$pkg_version")" || true
            if [[ -n "$cdate" ]]; then
                toml_github "$pkg_name" "$owner" "$repo" "$vtype"
                state_add_git "$pkg_name" "$cdate" "$pkg_version"
            else
                warn "$pkg_name: couldn't get commit date"
                toml_github "$pkg_name" "$owner" "$repo" "$vtype"
                state_add "$pkg_name" "$pkg_version"
            fi
        else
            toml_github "$pkg_name" "$owner" "$repo" "$vtype"
            state_add "$pkg_name" "$pkg_version"
        fi
        meta_add "$pkg_name" "$category" "$mk_file" "$pkg_version" "$display_site"
        count_checked+=1

    # Pattern: https://github.com/owner/repo[.git]
    elif [[ "$pkg_site" =~ ^https?://[^@]*github\.com/([^/]+)/([^/.]+) ]]; then
        local owner="${BASH_REMATCH[1]}" repo="${BASH_REMATCH[2]}"
        # Strip token prefix if present (private repos)
        display_site="https://github.com/$owner/$repo"

        if [[ "$vtype" == "commit" ]]; then
            local cdate
            cdate="$(get_commit_date "$display_site" "$pkg_version")" || true
            if [[ -n "$cdate" ]]; then
                toml_github "$pkg_name" "$owner" "$repo" "$vtype"
                state_add_git "$pkg_name" "$cdate" "$pkg_version"
            else
                warn "$pkg_name: couldn't get commit date"
                toml_github "$pkg_name" "$owner" "$repo" "$vtype"
                state_add "$pkg_name" "$pkg_version"
            fi
        else
            toml_github "$pkg_name" "$owner" "$repo" "$vtype"
            state_add "$pkg_name" "$pkg_version"
        fi
        meta_add "$pkg_name" "$category" "$mk_file" "$pkg_version" "$display_site"
        count_checked+=1

    # Pattern: https://gitlab.com/owner/repo
    elif [[ "$pkg_site" =~ ^https?://gitlab\.com/([^/]+)/([^/.]+) ]]; then
        local owner="${BASH_REMATCH[1]}" repo="${BASH_REMATCH[2]}"
        display_site="https://gitlab.com/$owner/$repo"
        toml_gitlab "$pkg_name" "$owner" "$repo" "$vtype"
        state_add "$pkg_name" "$pkg_version"
        meta_add "$pkg_name" "$category" "$mk_file" "$pkg_version" "$display_site"
        count_checked+=1

    # Pattern: https://<custom-gitlab>/owner/repo (e.g. voidpoint.io)
    elif [[ "$pkg_site" =~ ^https?://([^/]+)/([^/]+)/([^/]+)/-/archive ]]; then
        local host="${BASH_REMATCH[1]}" owner="${BASH_REMATCH[2]}" repo="${BASH_REMATCH[3]}"
        display_site="https://$host/$owner/$repo"
        toml_gitlab "$pkg_name" "$owner" "$repo" "$vtype" "$host"
        state_add "$pkg_name" "$pkg_version"
        meta_add "$pkg_name" "$category" "$mk_file" "$pkg_version" "$display_site"
        count_checked+=1

    # Pattern: git site method with any URL
    elif [[ "$pkg_site_method" == "git" ]] && [[ "$pkg_site" =~ ^https?:// ]]; then
        local clean_url="${pkg_site%.git}"
        display_site="$clean_url"

        # Try to detect GitHub/GitLab from git URL
        if [[ "$clean_url" =~ github\.com/([^/]+)/([^/]+) ]]; then
            local owner="${BASH_REMATCH[1]}" repo="${BASH_REMATCH[2]}"
            if [[ "$vtype" == "commit" ]]; then
                local cdate
                cdate="$(get_commit_date "$pkg_site" "$pkg_version")" || true
                if [[ -n "$cdate" ]]; then
                    toml_github "$pkg_name" "$owner" "$repo" "$vtype"
                    state_add_git "$pkg_name" "$cdate" "$pkg_version"
                else
                    toml_github "$pkg_name" "$owner" "$repo" "$vtype"
                    state_add "$pkg_name" "$pkg_version"
                fi
            else
                toml_github "$pkg_name" "$owner" "$repo" "$vtype"
                state_add "$pkg_name" "$pkg_version"
            fi
        elif [[ "$clean_url" =~ gitlab\.com/([^/]+)/([^/]+) ]]; then
            local owner="${BASH_REMATCH[1]}" repo="${BASH_REMATCH[2]}"
            toml_gitlab "$pkg_name" "$owner" "$repo" "$vtype"
            state_add "$pkg_name" "$pkg_version"
        else
            toml_git "$pkg_name" "$pkg_site"
            state_add "$pkg_name" "$pkg_version"
        fi
        meta_add "$pkg_name" "$category" "$mk_file" "$pkg_version" "$display_site"
        count_checked+=1

    else
        info "$pkg_name: unhandled site type: $pkg_site"
        count_skipped+=1
        return
    fi
}

# ── Scan directories ────────────────────────────────────────────────

scan_packages() {
    local targets=("${SCAN_TARGETS[@]}")
    if [[ ${#targets[@]} -eq 0 ]]; then
        targets=("$_ROOT/package")
    fi

    local mk_files=()
    for target in "${targets[@]}"; do
        if [[ -f "$target" ]]; then
            mk_files+=("$target")
        elif [[ -d "$target" ]]; then
            while IFS= read -r f; do
                mk_files+=("$f")
            done < <(find "$target" -type f -name "*.mk" | sort)
        else
            die "Not a file or directory: $target"
        fi
    done

    local total=${#mk_files[@]}
    echo -e "${C_DIM}Scanning $total .mk files...${C_RESET}" >&2

    local i=0
    for mk_file in "${mk_files[@]}"; do
        i=$((i + 1))
        # Show progress every 50 packages
        if [[ $((i % 50)) -eq 0 ]] || [[ $i -eq $total ]]; then
            printf "\r${C_DIM}  Scanning... %d/%d${C_RESET}" "$i" "$total" >&2
        fi
        parse_package "$mk_file"
    done
    printf "\r${C_DIM}  Scanned %d files: %d packages to check, %d skipped${C_RESET}\n" \
        "$total" "$count_checked" "$count_skipped" >&2
}

# ── Run nvchecker ───────────────────────────────────────────────────

run_nvchecker() {
    echo -e "${C_DIM}Running nvchecker on $count_checked packages...${C_RESET}" >&2

    # Run nvchecker from the script directory so relative paths work
    if ! (cd "$_SCRIPT_PATH" && nvchecker -c "$(basename "$_TOML_OUT")" 2>/dev/null); then
        # nvchecker may return non-zero even on partial success, continue
        true
    fi

    echo -e "${C_DIM}nvchecker complete.${C_RESET}" >&2
}

# ── Report rendering ───────────────────────────────────────────────

render_header() {
    local now
    now="$(date '+%Y-%m-%d %H:%M:%S')"
    echo ""
    echo -e "${C_BOLD}${C_BG_BLUE}${C_WHITE}                                                                      ${C_RESET}"
    echo -e "${C_BOLD}${C_BG_BLUE}${C_WHITE}                    REG-Linux Package Update Check                     ${C_RESET}"
    echo -e "${C_BOLD}${C_BG_BLUE}${C_WHITE}                         $now                          ${C_RESET}"
    echo -e "${C_BOLD}${C_BG_BLUE}${C_WHITE}                                                                      ${C_RESET}"
    echo ""
    echo -e "  ${C_DIM}$count_checked packages checked, $count_skipped skipped${C_RESET}"
    echo ""
}

render_category_header() {
    local label="$1"
    printf "${C_BOLD}${C_CYAN}── %-60s${C_RESET}──\n" "$label "
    echo ""
}

render_pkg_uptodate() {
    local pkg="$1" ver="$2"
    if [[ "$OPT_UPDATES_ONLY" == true ]]; then
        return
    fi
    printf "  ${C_GREEN}${SYM_OK}${C_RESET} ${C_BOLD}%-24s${C_RESET} ${C_DIM}%-20s == %-20s${C_RESET}\n" \
        "$pkg" "$ver" "$ver"
    count_uptodate+=1
}

render_pkg_update() {
    local pkg="$1" old_ver="$2" new_ver="$3" severity="$4"
    local sev_color="$C_YELLOW"
    [[ "$severity" == "major" ]] && sev_color="$C_RED"

    printf "  ${sev_color}${SYM_UP}${C_RESET} ${C_BOLD}%-24s${C_RESET} %-20s ${sev_color}-> %-20s${C_RESET} ${C_DIM}(%s)${C_RESET}\n" \
        "$pkg" "$old_ver" "$new_ver" "$severity"
    count_updates+=1

    case "$severity" in
        major)   count_major+=1 ;;
        minor)   count_minor+=1 ;;
        patch|commits) count_patch+=1 ;;
    esac
}

render_pkg_error() {
    local pkg="$1" msg="$2"
    printf "  ${C_RED}${SYM_ERR}${C_RESET} ${C_BOLD}%-24s${C_RESET} ${C_DIM}%s${C_RESET}\n" \
        "$pkg" "$msg"
    count_errors+=1
}

render_footer() {
    echo ""
    echo -e "${C_BOLD}══════════════════════════════════════════════════════════════════════${C_RESET}"
    echo ""
    printf "  ${C_BOLD}Summary:${C_RESET}  %d checked   " "$count_checked"
    printf "${C_GREEN}%d up-to-date${C_RESET}   " "$count_uptodate"
    printf "${C_YELLOW}%d updates${C_RESET}   " "$count_updates"
    printf "${C_RED}%d errors${C_RESET}\n" "$count_errors"

    if [[ $count_updates -gt 0 ]]; then
        echo ""
        printf "  Updates by severity:\n"
        printf "    ${C_RED}%d major${C_RESET}    ${C_YELLOW}%d minor${C_RESET}    ${C_DIM}%d patch/commits${C_RESET}\n" \
            "$count_major" "$count_minor" "$count_patch"
    fi
    echo ""
    echo -e "${C_BOLD}══════════════════════════════════════════════════════════════════════${C_RESET}"
    echo ""
}

# ── JSON output ─────────────────────────────────────────────────────

render_json() {
    local new_data old_data meta_data
    new_data="$(jq '.data // .' "$_NEW_JSON" 2>/dev/null || echo '{}')"
    old_data="$(jq '.data // .' "$_STATE_JSON" 2>/dev/null || echo '{}')"
    meta_data="$(cat "$_METADATA" 2>/dev/null || echo '{}')"

    jq -n \
        --arg date "$(date -Iseconds)" \
        --argjson old "$old_data" \
        --argjson new "$new_data" \
        --argjson meta "$meta_data" \
        '{
            date: $date,
            packages: [
                $meta | to_entries[] | {
                    name: .key,
                    category: .value.category,
                    current_version: .value.version,
                    latest_version: ($new[.key].version // null),
                    has_update: (($new[.key].version // .value.version) != ($old[.key].version // .value.version)),
                    site: .value.site
                }
            ]
        }'
}

# ── Main report logic ───────────────────────────────────────────────

generate_report() {
    if [[ "$OPT_JSON" == true ]]; then
        render_json
        return
    fi

    # nvchecker output wraps data under .data for both old and new
    local new_data old_data meta_data
    new_data="$(jq '.data // .' "$_NEW_JSON" 2>/dev/null || echo '{}')"
    old_data="$(jq '.data // .' "$_STATE_JSON" 2>/dev/null || echo '{}')"
    meta_data="$(cat "$_METADATA" 2>/dev/null || echo '{}')"

    render_header

    # Get sorted unique categories from metadata
    local categories
    categories="$(jq -r '.[].category' "$_METADATA" | sort -u)"

    local errors_buf=""

    for cat in $categories; do
        local cat_has_output=false
        local cat_buf=""

        # Get packages in this category, sorted by name
        local pkgs
        pkgs="$(jq -r "to_entries[] | select(.value.category == \"$cat\") | .key" "$_METADATA" | sort)"

        for pkg in $pkgs; do
            local old_ver new_ver old_rev
            old_ver="$(jq -r --arg p "$pkg" '.[$p].version // empty' <<< "$old_data")" || true
            old_rev="$(jq -r --arg p "$pkg" '.[$p].revision // empty' <<< "$old_data")" || true
            new_ver="$(jq -r --arg p "$pkg" '.[$p].version // empty' <<< "$new_data")" || true
            local orig_ver
            orig_ver="$(jq -r --arg p "$pkg" '.[$p].version // empty' "$_METADATA")" || true

            # Use original version for display
            local display_old="$orig_ver"

            if [[ -z "$new_ver" ]]; then
                # nvchecker returned nothing — probably an error
                errors_buf+="$(printf "  ${C_RED}${SYM_ERR}${C_RESET} ${C_BOLD}%-24s${C_RESET} ${C_DIM}No response from nvchecker${C_RESET}\n" "$pkg")"$'\n'
                count_errors+=1
                continue
            fi

            # For commit-based: old_ver is a date, new_ver is also a date
            # Show abbreviated hashes instead
            if [[ -n "$old_rev" ]]; then
                display_old="${old_rev:0:7}.."
            fi

            # Check if versions differ
            if [[ "$old_ver" == "$new_ver" ]]; then
                if [[ "$OPT_UPDATES_ONLY" != true ]]; then
                    cat_buf+="$(printf "  ${C_GREEN}${SYM_OK}${C_RESET} ${C_BOLD}%-24s${C_RESET} ${C_DIM}%-20s == %-20s${C_RESET}\n" \
                        "$pkg" "$display_old" "$display_old")"$'\n'
                    cat_has_output=true
                fi
                count_uptodate+=1
            else
                local display_new="$new_ver"
                local new_rev
                new_rev="$(jq -r --arg p "$pkg" '.[$p].revision // empty' <<< "$new_data")" || true
                if [[ -n "$new_rev" ]] && [[ -n "$old_rev" ]]; then
                    display_new="${new_rev:0:7}.."
                fi

                local severity
                severity="$(classify_bump "$display_old" "$display_new")"
                local sev_color="$C_YELLOW"
                [[ "$severity" == "major" ]] && sev_color="$C_RED"

                cat_buf+="$(printf "  ${sev_color}${SYM_UP}${C_RESET} ${C_BOLD}%-24s${C_RESET} %-20s ${sev_color}-> %-20s${C_RESET} ${C_DIM}(%s)${C_RESET}\n" \
                    "$pkg" "$display_old" "$display_new" "$severity")"$'\n'
                cat_has_output=true
                count_updates+=1
                case "$severity" in
                    major)          count_major+=1 ;;
                    minor)          count_minor+=1 ;;
                    patch|commits)  count_patch+=1 ;;
                esac
            fi
        done

        if [[ "$cat_has_output" == true ]]; then
            render_category_header "$(category_label "$cat")"
            echo -e "$cat_buf"
        fi
    done

    # Errors section
    if [[ -n "$errors_buf" ]]; then
        render_category_header "Errors ($count_errors)"
        echo -e "$errors_buf"
    fi

    render_footer
}

# ── Main ────────────────────────────────────────────────────────────

main() {
    parse_args "$@"

    # Check dependencies
    command -v nvchecker >/dev/null 2>&1 || die "nvchecker not found. Install with: pip install nvchecker"
    command -v jq >/dev/null 2>&1 || die "jq not found. Install with: apt install jq"

    # Setup GitHub token in keyfile
    if [[ ! -f "$_KEYFILE" ]]; then
        local gh_token="${GITHUB_TOKEN:-}"
        # Try gh CLI if no env var
        if [[ -z "$gh_token" ]] && command -v gh >/dev/null 2>&1; then
            gh_token="$(gh auth token 2>/dev/null)" || true
        fi
        if [[ -n "$gh_token" ]]; then
            cat > "$_KEYFILE" << EOF
[keys]
github = "$gh_token"
EOF
            echo -e "${C_DIM}Created keyfile.toml from GitHub token${C_RESET}" >&2
        else
            warn "No GitHub token found. API rate limit is 60 req/hr. Set GITHUB_TOKEN or run 'gh auth login'."
        fi
    fi

    init_toml
    scan_packages
    run_nvchecker
    generate_report

    # Apply updates if --update was given
    if [[ -n "$OPT_UPDATE" ]]; then
        apply_updates
    fi

    # Cleanup temp files
    rm -f "$_METADATA" 2>/dev/null || true
}

# ── Update .mk files ───────────────────────────────────────────────

apply_updates() {
    local new_data old_data meta_data
    new_data="$(jq '.data // .' "$_NEW_JSON" 2>/dev/null || echo '{}')"
    old_data="$(jq '.data // .' "$_STATE_JSON" 2>/dev/null || echo '{}')"
    meta_data="$(cat "$_METADATA" 2>/dev/null || echo '{}')"

    # Build list of packages to update
    local update_pkgs=()
    if [[ "$OPT_UPDATE" == "ALL" ]]; then
        # All packages that have updates
        while IFS= read -r pkg; do
            [[ -n "$pkg" ]] && update_pkgs+=("$pkg")
        done < <(jq -r 'to_entries[] | .key' "$_METADATA")
    else
        IFS=',' read -ra update_pkgs <<< "$OPT_UPDATE"
    fi

    local updated=0
    echo "" >&2

    for pkg in "${update_pkgs[@]}"; do
        local old_ver new_ver new_rev mk_file orig_ver
        old_ver="$(jq -r --arg p "$pkg" '.[$p].version // empty' <<< "$old_data")" || true
        new_ver="$(jq -r --arg p "$pkg" '.[$p].version // empty' <<< "$new_data")" || true
        new_rev="$(jq -r --arg p "$pkg" '.[$p].revision // empty' <<< "$new_data")" || true
        mk_file="$(jq -r --arg p "$pkg" '.[$p].mk_file // empty' "$_METADATA")" || true
        orig_ver="$(jq -r --arg p "$pkg" '.[$p].version // empty' "$_METADATA")" || true

        # Skip if no update or missing data
        if [[ -z "$new_ver" ]] || [[ "$old_ver" == "$new_ver" ]]; then
            continue
        fi
        if [[ -z "$mk_file" ]] || [[ ! -f "$mk_file" ]]; then
            warn "$pkg: .mk file not found: $mk_file"
            continue
        fi

        # Determine what to write: for commit-based packages, use the revision (commit hash)
        # For tag-based packages, use the version (tag name)
        local write_ver="$new_ver"
        if [[ "$orig_ver" =~ ^[a-f0-9]{40}$ ]] && [[ -n "$new_rev" ]]; then
            write_ver="$new_rev"
        fi

        # Find the VERSION variable name
        local br_name
        br_name="$(echo "${pkg^^}" | tr '-' '_')"
        local ver_var="${br_name}_VERSION"

        # Check that the current version in the file matches what we expect
        local file_ver
        file_ver="$(get_mk_var "$mk_file" "$ver_var")"
        if [[ "$file_ver" != "$orig_ver" ]]; then
            warn "$pkg: version in $mk_file ($file_ver) != expected ($orig_ver), skipping"
            continue
        fi

        # Do the replacement
        sed -i "s|^\(${ver_var}[[:space:]]*=[[:space:]]*\).*|\1${write_ver}|" "$mk_file"

        # Verify
        local verify_ver
        verify_ver="$(get_mk_var "$mk_file" "$ver_var")"
        if [[ "$verify_ver" == "$write_ver" ]]; then
            echo -e "  ${C_GREEN}${SYM_OK}${C_RESET} ${C_BOLD}$pkg${C_RESET}: $orig_ver -> $write_ver  ${C_DIM}($mk_file)${C_RESET}"
            updated=$((updated + 1))
        else
            echo -e "  ${C_RED}${SYM_ERR}${C_RESET} ${C_BOLD}$pkg${C_RESET}: sed failed (got '$verify_ver')"
        fi
    done

    if [[ $updated -gt 0 ]]; then
        echo ""
        echo -e "  ${C_GREEN}Updated $updated package(s)${C_RESET}"
    else
        echo -e "  ${C_DIM}No packages updated${C_RESET}"
    fi
    echo ""
}

main "$@"
