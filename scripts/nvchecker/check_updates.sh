#! /bin/bash
#~ set -x

# TODO
# * commit versions need a timestamp otherwise nvcmp is useless
# * in a call github method or just an URL, detect prefixes or suffixes
# * some repos don't use the master default branch name
# * when checking souce type for a commit, gitlab may not well be handled

_SCRIPT_PATH="$(dirname "$0")"
# this file holds some nvchecker toml parameters that extend the default behaviour of this script
_OVERRIDES_FILE="$_SCRIPT_PATH"/overrides.conf
# Simple json for nvchecker tht lists buildroot packages versions
_BUILDROOT_JS="$_SCRIPT_PATH"/buildroot_state.json
# Packages you don't want to be checked by nvchecker
_PACKAGES_EXCLUDE="$_SCRIPT_PATH"/packages.exclude
# Default toml output file
_TOML_OUT="$_SCRIPT_PATH"/nvchecker.toml
# Basic log level
_LOG_LEVEL=1

packages_parsed=0
packages_skipped=0

log_info() {
    [[ _LOG_LEVEL -lt 2 ]] && return
    log_ "(I) $@"
}

log_warn() {
    [[ _LOG_LEVEL -lt 1 ]] && return
    log_ "(W) $@"
}

log_error() {
    [[ _LOG_LEVEL -le 0 ]] && return
    log_ "(E) $@"
}

log_() {
    echo "$@" >&2
}

buildroot_json_header() {
    echo '{
  "version": 2,
  "data": {
  }
}' > "$_BUILDROOT_JS"
}

# $1: package name
# $2: version
add_package_to_buildroot_json() {
    [[ -e "$_BUILDROOT_JS" ]] && \
    jq \
        --arg package "$1" \
        --arg version "$2" \
        '.data[$package] = {version: $version}' "$_BUILDROOT_JS" > tmp.$$.json && mv tmp.$$.json "$_BUILDROOT_JS"
}

# $1: package name
# $2: version
# $3: revision
add_git_package_to_buildroot_json() {
    [[ -e "$_BUILDROOT_JS" ]] && \
    jq \
        --arg package "$1" \
        --arg version "$2" \
        --arg revision "$3" \
        '.data[$package] = {version: $version, revision: $revision}' "$_BUILDROOT_JS" > tmp.$$.json && mv tmp.$$.json "$_BUILDROOT_JS"
}

# $1: the https:// git repo
# $2: the commit id
get_commit_date() {
    # Eventually remove --depth=1 if the commit is too deep in the history
    git -c init.defaultBranch=tmp init --quiet /tmp/.git$$ && \
    git -C /tmp/.git$$ fetch --quiet --depth=1 --filter=blob:none "$1" "$2" && \
    git -C /tmp/.git$$ show -s --format=%ci FETCH_HEAD | xargs -I{} date -u -d {} +%Y%m%d.%H%M%S
    local rc=$?
    rm -rf /tmp/.git$$ 2>/dev/null
    return "$rc"
}

toml_header() {
    cat << EOF > "$_TOML_OUT"
[__config__]
keyfile = "keyfile.toml"
max_concurrency = 20
oldver = "$(basename $_BUILDROOT_JS)"
newver = "sources_tip.json"

EOF
}

package_has_overrides() {
    grep -q "^${1}\..*=.*$" "$_OVERRIDES_FILE"
}
get_package_overrides() {
    grep "^${1}\..*=.*$" "$_OVERRIDES_FILE" | cut -d '.' -f2- | sed 's/=/ = /g'
}

# $1 : package name
# $2 : repo owner
# $3 : repo name
# $4 : version type : tag/commit -> can't use commit afterall
get_nvchecker_pkg_toml_github() {
  local details='github = "'"$2/$3"'"'
  if [[ "$4" == "version" ]] ; then
    # Make sure overrides don't need a different approach
    grep -qE "^${1}\.(use_max_release|use_latest_tag)=" "$_OVERRIDES_FILE" || details+=$'\n''use_latest_release = "true"'
  else
    #~ details+=$'\n''branch = "master"'
    #~ details+=$'\n''use_commit = "true"'
    true
  fi
  get_nvchecker_pkg_toml "$1" "github" "$details"
}

# $1 : package name
# $2 : repo owner
# $3 : repo name
# $4 : version type : tag/commit
get_nvchecker_pkg_toml_gitlab() {
    local details='gitlab = "'"$2/$3"'"'
    if [[ "$4" == "version" ]] ; then
        details+=$'\n''use_max_tag = "true"'
    else
        details+=$'\n''branch = "master"'
    fi
    get_nvchecker_pkg_toml "$1" "gitlab" "$details"
}

# $1 : package name
# $2 : url
# $3 : commit id
get_nvchecker_pkg_toml_git() {
    local details='git = "'"$2"'"'
    local version=""
    if ! version="$(get_commit_date "$2" "$3")" ; then
        log_error "$1: couldn't get commit date"
        packages_skipped=$((packages_skipped+1))
        return 1
    fi
    #~ details+=$'\n''version = "'$version'"'
    #~ details+=$'\n''revision = "'$3'"'
    #~ details+=$'\n''use_max_tag = "true"'
    #~ details+=$'\n''use_commit = "true"'
    get_nvchecker_pkg_toml "$1" "git" "$details"
    add_git_package_to_buildroot_json "$1" "$version" "$3"
}

get_nvchecker_pkg_toml() {
    cat <<EOF >> "$_TOML_OUT"
[$1]
source = "$2"
EOF
    local pkg_name="$1"
    shift ; shift
    echo "$@" >> "$_TOML_OUT"
    get_package_overrides "$pkg_name"  >> "$_TOML_OUT"
    echo  >> "$_TOML_OUT"
}

get_mk_parameter_value() {
    # awk is here to trim spaces left and right
    local value="$(grep "^$2[[:space:]]*=" "$1" | cut -d '=' -f2 | awk '{$1=$1;print}')"
    # In the case the value is on 2 lines
    if [[ $value = '\' ]] ; then
        grep -A1 "^$2[[:space:]]*=" "$1" | tail -1 | cut -d '=' -f2 | awk '{$1=$1;print}'
    else
        echo "$value"
    fi
}
#
# Checks a .mk file for all the required infos for nvchecker toml section
#
parse_package() {
    local mk_file="$1"
    local pkg_name="$(basename "$mk_file")"
    pkg_name="${pkg_name%.mk}"
    local br_pkg_name="$(echo ${pkg_name^^} | tr '-' '_')"
    local pkg_method=""
    local pkg_site_method=""
    local pkg_owner=""
    local pkg_repo=""
    local pkg_version_type="version"

    # Skip excluded packages
    if $(grep -q "$pkg_name" "$_PACKAGES_EXCLUDE") ; then
        log_warn "$pkg_name must be skipped"
        packages_skipped=$((packages_skipped+1))
        return
    fi

    local pkg_version="$(get_mk_parameter_value "$mk_file" "${br_pkg_name}_VERSION")"
    local pkg_site_method="$(get_mk_parameter_value "$mk_file" "${br_pkg_name}_SITE_METHOD")"

    # If the version comes from another package, do what it takes
    # That's the case of libretro-flycast and libretro-applewin just to name these
    # dirty, I know ... Using buildroot would be too slow
    if [[ $pkg_version =~ ^\$\(.*_VERSION\)$ ]] ; then
        log_warn "$pkg_name: version comes from another package"
        local original_pkg="$(echo "$pkg_version" | grep -oE '[A-Z_]+')"
        local original_mk="$((cd "$_SCRIPT_PATH"/../.. && git grep -E "^[[:space:]]*$original_pkg[[:space:]]*=") | cut -d ':' -f 1)"
        if [[ -z "$original_mk" ]] ; then
            log_error "$pkg_name: couldn't find the real version"
            packages_skipped=$((packages_skipped+1))
            return
        fi
        pkg_version="$(get_mk_parameter_value "$original_mk" "${original_pkg}")"
    fi

    # Check version if it's a commit hash or not 
    if echo "$pkg_version" | grep -qE "[a-z0-9]{40}" ; then
        log_info "$pkg_name: Version is a commit hash, will use git source"
        pkg_version_type="commit"
    elif [[ "$pkg_version" =~ ^[a-z][0-9]+ ]] ; then
        log_info "$pkg_name: Version starts with ${pkg_version:0:1} and could be simplified"
    fi

    local pkg_site="$(get_mk_parameter_value "$mk_file" "${br_pkg_name}_SITE")"
    # Check the source type, but use commitTTTTT instead of commit to skip that part
    # nvchecker will check for tags. If none, gets the last commit from the default branch
    if [[ "$pkg_version_type" == "commit" ]] ; then
        local pkg_url=""
        # We need to know how the source is to decide accordingly
        if [[ $pkg_site =~ ^\$\("call github,".* ]] ; then
            pkg_owner="$(echo ''$pkg_site'' | cut -d ',' -f2)"
            pkg_repo="$(echo ''$pkg_site'' | cut -d ',' -f3)"
            pkg_url="https://github.com/$pkg_owner/$pkg_repo"
            get_nvchecker_pkg_toml_github "$pkg_name" "$pkg_owner" "$pkg_repo" "$pkg_version_type"
            if ! version="$(get_commit_date "$pkg_url" "$pkg_version")" ; then
                log_error "$1: couldn't get commit date"
                packages_skipped=$((packages_skipped+1))
                return 1
            fi
            add_git_package_to_buildroot_json "$pkg_name" "$version" "$pkg_version"
            packages_parsed=$((packages_parsed+1))
        elif [[ $pkg_site =~ ^http[s]?://github.com/.* ]] ; then
            pkg_owner="$(echo ''$pkg_site'' | cut -d '/' -f4)"
            pkg_repo="$(echo ''$pkg_site'' | cut -d '/' -f5 | sed 's/.git$//')"
            pkg_url="https://github.com/$pkg_owner/$pkg_repo"
            get_nvchecker_pkg_toml_github "$pkg_name" "$pkg_owner" "$pkg_repo" "$pkg_version_type"
            if ! version="$(get_commit_date "$pkg_url" "$pkg_version")" ; then
                log_error "$1: couldn't get commit date"
                packages_skipped=$((packages_skipped+1))
                return 1
            fi
            add_git_package_to_buildroot_json "$pkg_name" "$version" "$pkg_version"
            packages_parsed=$((packages_parsed+1))
        elif [[ $pkg_site =~ ^http[s]?.* ]] ; then
            
            log_error "$pkg_name: git source on a commit not yet handled pkg_url=${pkg_site%.git}"
            #~ get_nvchecker_pkg_toml_git "$pkg_name" "$pkg_url" "$pkg_version"
            packages_skipped=$((packages_skipped+1))
        else
            log_error "$pkg_name: Unknow git source type '$pkg_site', skipping"
            packages_skipped=$((packages_skipped+1))
            return
        fi
    # If call github
    elif [[ $pkg_site =~ ^\$\("call github,".* ]] ; then
        log_info "$pkg_name: Github call source"
        pkg_method="github"
        pkg_owner="$(echo ''$pkg_site'' | cut -d ',' -f2)"
        pkg_repo="$(echo ''$pkg_site'' | cut -d ',' -f3)"
        get_nvchecker_pkg_toml_github "$pkg_name" "$pkg_owner" "$pkg_repo" "$pkg_version_type"
        add_package_to_buildroot_json "$pkg_name" "$pkg_version"
        packages_parsed=$((packages_parsed+1))
    # if https://github.com
    elif [[ $pkg_site =~ ^http[s]?://github.com/.* ]] ; then
        log_info "$pkg_name: Github https source"
        pkg_method="github"
        pkg_owner="$(echo ''$pkg_site'' | cut -d '/' -f4)"
        pkg_repo="$(echo ''$pkg_site'' | cut -d '/' -f5 | sed 's/.git$//')"
        get_nvchecker_pkg_toml_github "$pkg_name" "$pkg_owner" "$pkg_repo" "$pkg_version_type"
        add_package_to_buildroot_json "$pkg_name" "$pkg_version"
        packages_parsed=$((packages_parsed+1))
    # if https://gitlab.com
    elif [[ $pkg_site =~ ^http[s]?://gitlab.com/.* ]] ; then
        log_info "$pkg_name: gitlab https source"
        pkg_method="gitlab"
        pkg_owner="$(echo ''$pkg_site'' | cut -d '/' -f4)"
        pkg_repo="$(echo ''$pkg_site'' | cut -d '/' -f5)"
        get_nvchecker_pkg_toml_gitlab "$pkg_name" "$pkg_owner" "$pkg_repo" "$pkg_version_type"
        add_package_to_buildroot_json "$pkg_name" "$pkg_version"
        packages_parsed=$((packages_parsed+1))
    # if _SITE_METHOD = git
    elif [[ "$pkg_site_method" == "git" ]] ; then
        log_info "$pkg_name: site method is git, not yet handled" >&2
    elif [[ -n "$pkg_site_method" ]] ; then
        log_error "$pkg_name: site method is unhandled"
        packages_skipped=$((packages_skipped+1))
    # else ... Errr ... we're doomed
    else
        log_error "$pkg_name: Unhandled source management method"
        packages_skipped=$((packages_skipped+1))
    fi
}


#
# Parse a complete folder
#
parse_dir() {
    #~ for f in $(find "$1" -type f -name "*.mk" | grep -v 'yquake2' | sort) ; do
    for f in $(find "$1" -type f -name "*.mk" | sort) ; do
        parse_package "$f"
    done
}

test_single() {
    # Useful commands to find test cases from the scripts/nvchecker folder
    # (cd ../.. && git grep -E '_VERSION[[:space:]]+=[[:space:]]+[a-z]{1}[0-9.]+' | grep -vE "[a-z0-9]{40}")
    # -> lists any version that is not a commit hash

    # version has a heading v, call github
    parse_package "$_SCRIPT_PATH"/../../package/retroarch/retroarch/retroarch.mk
    # version is a commit, call github
    parse_package "$_SCRIPT_PATH"/../../package/emulators/libretro/libretro-genesisplusgx/libretro-genesisplusgx.mk
    # versrsion has a heading v, SITE starts with https://github.com, METHOD is git
    parse_package "$_SCRIPT_PATH"/../../package/emulators/flycast/flycast.mk
    # SITE starts with gitlab.com
    # toml needs: exclude_regex = "v.*\\+cicd[0-9]{1}$"
    parse_package "$_SCRIPT_PATH"/../../package/engines/solarus-engine/solarus-engine.mk
    # _VERSION starts with n
    parse_package "$_SCRIPT_PATH"/../../package/batocera/gpu/nv-codec-headers/nv-codec-headers.mk
    # Complex version like v3.6.0-1227-ecd032e + prefixed by v
    parse_package "$_SCRIPT_PATH"/../../package/libraries/libpinmame/libpinmame.mk
    # Weird version as well like v10.8.0-2051-28dd6c3
    parse_package "$_SCRIPT_PATH"/../../package/engines/vpinball/vpinball.mk
    # Version prefixed by g
    parse_package "$_SCRIPT_PATH"/../../package/ports/gzdoom/gzdoom.mk
    # etlegacy only has tags, no release -> requires use_latest_tag = "true"
    parse_package "$_SCRIPT_PATH"/../../package/ports/etlegacy/etlegacy.mk
    # duckstation{,-gpl-mini} returns no version value if no override
    parse_package "$_SCRIPT_PATH"/../../package/ports/augustus/augustus.mk
    # ioquake3 main branch is not master on github
    parse_package "$_SCRIPT_PATH"/../../package/ports/ioquake3/ioquake3.mk
    # eduke32 is a gitlab site but not using git site method
    parse_package "$_SCRIPT_PATH"/../../package/ports/eduke32/eduke32.mk
}

parse_all() {
    toml_header
    buildroot_json_header

    # yquake2-* are virtual packages and miserably fail for now
    parse_dir "$_SCRIPT_PATH"/../../package/ports # works
    parse_dir "$_SCRIPT_PATH"/../../package/emulators # works
    parse_dir "$_SCRIPT_PATH"/../../package/engines # works
}

[[ -e "$_TOML_OUT" ]] && rm "$_TOML_OUT"
# $1 is a .mk or path
if [[ -z "$1" ]] ; then
    parse_all
elif [[ -d "$1" ]] ; then
    toml_header
    buildroot_json_header
    parse_dir "$1"
elif [[ -f "$1" ]] ; then
    toml_header
    buildroot_json_header
    parse_package "$1"
else
    log_error "$1 couldn't be processed. Not a valid dir or file"
    exit 1
fi

# Stats
echo "Packages parsed: $packages_parsed / skipped: $packages_skipped" >&2

(cd "$_SCRIPT_PATH" && nvchecker -c "$(basename "$_TOML_OUT")")
