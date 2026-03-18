#!/usr/bin/env bash
# QT6updatehashes.sh - Update Qt6 package hash files to the current version in qt6.mk
#
# Run from the root of the REG-Linux repository:
#   ./scripts/linux/prebuild/QT6updatehashes.sh
#
# Official tarball packages: sha256 fetched from download.qt.io.
#
# Git-sourced packages (qt6mqtt, qt6opcua, ...):
#   The hash is computed locally by replicating Buildroot's exact git download
#   + mk_tar_gz recipe from buildroot/support/download/{git,helpers}:
#     1. Shallow-clone the repo at the version tag (tries v<VER> then <VER>)
#     2. Record the commit timestamp (git log -1 --pretty=format:%ci)
#     3. Build a reproducible POSIX tar (sorted file list, owner=0, mtime=commit)
#     4. Compress with gzip -6 -n
#     5. sha256sum the result
#   The tarball is named <pkg>-<version><BR_FMT_VERSION_git>.tar.gz
#   where BR_FMT_VERSION_git is read from buildroot/package/pkg-download.mk.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"

QT6_MK="$REPO_ROOT/buildroot/package/qt6/qt6.mk"
QT6_PKG_DIR="$REPO_ROOT/buildroot/package/qt6"

# ---------------------------------------------------------------------------
# Extract version from qt6.mk
# ---------------------------------------------------------------------------
QT6_VERSION_MAJOR=$(grep '^QT6_VERSION_MAJOR[[:space:]]*=' "$QT6_MK" \
    | sed 's/[^=]*=[[:space:]]*//' | tr -d ' \t')

QT6_VERSION_RAW=$(grep '^QT6_VERSION[[:space:]]*=' "$QT6_MK" | head -1 \
    | sed 's/[^=]*=[[:space:]]*//' | tr -d ' \t')

QT6_VERSION=$(echo "$QT6_VERSION_RAW" \
    | sed "s/\$(QT6_VERSION_MAJOR)/$QT6_VERSION_MAJOR/g")

# git:// base URL for Qt git repos (from QT6_GIT in qt6.mk), converted to https://
QT6_GIT_BASE=$(grep '^QT6_GIT[[:space:]]*=' "$QT6_MK" \
    | sed 's/[^=]*=[[:space:]]*//' | tr -d ' \t' \
    | sed 's|^git://|https://|')

# Buildroot git tarball format-version suffix (e.g. "-git4")
BR_FMT_GIT=$(grep 'BR_FMT_VERSION_git' \
    "$REPO_ROOT/buildroot/package/pkg-download.mk" \
    | sed 's/.*=[[:space:]]*//' | tr -d ' \t')

QT6_BASE_URL="https://download.qt.io/official_releases/qt/${QT6_VERSION_MAJOR}/${QT6_VERSION}/submodules"

echo "Qt6 target version : $QT6_VERSION  (major: $QT6_VERSION_MAJOR)"
echo "Git format suffix  : $BR_FMT_GIT"
echo "Download base URL  : $QT6_BASE_URL"
echo ""

updated=0
skipped=0
failed=0

# ---------------------------------------------------------------------------
# mk_tar_gz: replicate buildroot/support/download/helpers exactly
#   $1 = source directory (git working tree)
#   $2 = basename (prefix inside archive, e.g. qt6mqtt-6.10.2)
#   $3 = commit date (ISO8601 string from git log)
#   $4 = output .tar.gz path
# ---------------------------------------------------------------------------
mk_tar_gz() {
    local in_dir="$1" base_dir="$2" date="$3" out="$4"

    # Normalise to whole-second UTC, matching Buildroot's date -d ... -u +...
    date="$(date -d "${date}" -u +%Y-%m-%dT%H:%M:%S+00:00)"

    local pax_options="delete=atime,delete=ctime,delete=mtime"
    pax_options+=",exthdr.name=%d/PaxHeaders/%f,exthdr.mtime={${date}}"

    local tmp
    tmp="$(mktemp)"

    pushd "${in_dir}" >/dev/null

    # Sorted file list excluding .git/
    find . -not -type d -and -not -path './.git/*' \
        | LC_ALL=C sort > "${tmp}.sorted"

    tar cf - \
        --transform="s#^\./#${base_dir}/#S" \
        --numeric-owner --owner=0 --group=0 \
        --mtime="${date}" \
        --format=posix \
        --pax-option="${pax_options}" \
        --mode='go=u,go-w' \
        -T "${tmp}.sorted" \
        > "${tmp}.tar"

    gzip -6 -n < "${tmp}.tar" > "${out}"

    rm -f "${tmp}" "${tmp}.sorted" "${tmp}.tar"
    popd >/dev/null
}

# ---------------------------------------------------------------------------
# Handle a git-sourced package: clone, build tarball, compute sha256
#   $1 = package name (e.g. qt6mqtt)
#   $2 = path to hash file
# Returns 0 on success and prints UPDATED/FAIL; updates hash file in place.
# ---------------------------------------------------------------------------
handle_git_package() {
    local pkg_name="$1"
    local hash_file="$2"

    # Find the main tarball sha256 line
    local main_line
    main_line=$(grep '^sha256' "$hash_file" \
        | grep -v ' LICENSES/' \
        | grep -v ' src/' \
        | head -1 || true)

    if [[ -z "$main_line" ]]; then
        echo "SKIP  (no tarball sha256 line)"
        skipped=$((skipped + 1))
        return
    fi

    local old_filename
    old_filename=$(awk '{print $3}' <<< "$main_line")

    # Extract old version: pkg-VERSION-gitN.tar.gz
    local old_version
    old_version=$(echo "$old_filename" \
        | sed -n "s/^${pkg_name}-\(.*\)${BR_FMT_GIT}\.tar\.gz/\1/p")

    if [[ -z "$old_version" ]]; then
        echo "SKIP  (cannot parse version from: $old_filename)"
        skipped=$((skipped + 1))
        return
    fi

    if [[ "$old_version" == "$QT6_VERSION" ]]; then
        echo "OK    (already at $QT6_VERSION)"
        return
    fi

    # Get git URL from the .mk file, expand $(QT6_GIT)
    local mk_file
    mk_file="$(dirname "$hash_file")/${pkg_name}.mk"
    local pkg_upper
    pkg_upper=$(echo "$pkg_name" | tr '[:lower:]' '[:upper:]' | tr '-' '_')

    local git_url_raw
    git_url_raw=$(grep "^${pkg_upper}_SITE[[:space:]]*=" "$mk_file" \
        | sed 's/[^=]*=[[:space:]]*//' | tr -d ' \t')

    # Expand $(QT6_GIT) → https://...
    local git_url
    git_url="${git_url_raw/\$(QT6_GIT)/$QT6_GIT_BASE}"

    if [[ -z "$git_url" || "$git_url" == "$git_url_raw" ]]; then
        echo "FAIL  (cannot resolve git URL: $git_url_raw)"
        failed=$((failed + 1))
        return
    fi

    local basename="${pkg_name}-${QT6_VERSION}"
    local new_filename="${basename}${BR_FMT_GIT}.tar.gz"
    local tmp_dir
    tmp_dir="$(mktemp -d)"
    local clone_dir="$tmp_dir/src"
    local output="$tmp_dir/$new_filename"

    # Clone at $QT6_VERSION — same CSET Buildroot uses
    printf "\n    Cloning %s at %s ... " "$git_url" "$QT6_VERSION"
    if ! git clone -q --depth=1 --branch "$QT6_VERSION" "$git_url" "$clone_dir" \
            2>/dev/null; then
        echo "FAIL"
        echo "FAIL  (git clone failed: $git_url at $QT6_VERSION)"
        rm -rf "$tmp_dir"
        failed=$((failed + 1))
        return
    fi
    echo "OK"

    # Get commit date for reproducible tarball mtime
    local commit_date
    commit_date=$(git -C "$clone_dir" log -1 --pretty=format:%ci)

    printf "    Building tarball %s ... " "$new_filename"
    if ! mk_tar_gz "$clone_dir" "$basename" "$commit_date" "$output"; then
        echo "FAIL"
        rm -rf "$tmp_dir"
        echo "FAIL  (tarball creation failed)"
        failed=$((failed + 1))
        return
    fi
    echo "OK"

    local new_hash
    new_hash=$(sha256sum "$output" | awk '{print $1}')

    rm -rf "$tmp_dir"

    # Update hash file: replace old tarball sha256 line
    sed -i "s|^sha256  .*  ${old_filename}$|sha256  ${new_hash}  ${new_filename}|" \
        "$hash_file"

    echo "UPDATED  $old_version -> $QT6_VERSION  (${new_hash:0:16}...)"
    updated=$((updated + 1))
}

# ---------------------------------------------------------------------------
# Process each hash file
# ---------------------------------------------------------------------------
for hash_file in "$QT6_PKG_DIR"/*/*.hash; do
    pkg_name=$(basename "$(dirname "$hash_file")")
    printf "%-30s  " "$pkg_name"

    # ---- Git-sourced packages (Locally computed) ----
    if grep -q '^# Locally computed' "$hash_file"; then
        handle_git_package "$pkg_name" "$hash_file"
        continue
    fi

    # ---- Official tarball packages ----
    main_line=$(grep '^sha256' "$hash_file" \
        | grep -v ' LICENSES/' \
        | grep -v ' src/' \
        | head -1 || true)

    if [[ -z "$main_line" ]]; then
        echo "SKIP  (no tarball sha256 line found)"
        skipped=$((skipped + 1))
        continue
    fi

    old_filename=$(echo "$main_line" | awk '{print $3}')

    old_version=$(echo "$old_filename" \
        | sed -n 's/.*-everywhere-src-\(.*\)\.tar\.xz/\1/p')

    if [[ -z "$old_version" ]]; then
        echo "SKIP  (cannot extract version from filename: $old_filename)"
        skipped=$((skipped + 1))
        continue
    fi

    if [[ "$old_version" == "$QT6_VERSION" ]]; then
        echo "OK    (already at $QT6_VERSION)"
        continue
    fi

    new_filename="${old_filename/$old_version/$QT6_VERSION}"
    sha256_url="${QT6_BASE_URL}/${new_filename}.sha256"

    if ! response=$(curl -fsSL --retry 3 --retry-delay 2 "$sha256_url" 2>/dev/null); then
        echo "FAIL  (could not fetch $sha256_url)"
        failed=$((failed + 1))
        continue
    fi

    new_hash=$(echo "$response" | awk '{print $1}')
    if [[ -z "$new_hash" || ${#new_hash} -ne 64 ]]; then
        echo "FAIL  (unexpected response from $sha256_url: '$response')"
        failed=$((failed + 1))
        continue
    fi

    sed -i "s|^# Hash from:.*|# Hash from: ${sha256_url}|" "$hash_file"
    sed -i "s|^sha256  .*  ${old_filename}$|sha256  ${new_hash}  ${new_filename}|" \
        "$hash_file"

    echo "UPDATED  $old_version -> $QT6_VERSION  (${new_hash:0:16}...)"
    updated=$((updated + 1))
done

echo ""
echo "Results: $updated updated, $skipped skipped, $failed failed"

if [[ $failed -gt 0 ]]; then
    echo "WARNING: $failed package(s) could not be updated — check output above." >&2
    exit 1
fi
