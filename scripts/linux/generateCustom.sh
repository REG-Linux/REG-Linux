#!/bin/bash
# Credits: Recalbox Team

### Global variables ###

BUILDROOT_DIR=${BUILDROOT_DIR:-"./buildroot"}
CUSTOM_DIR=${CUSTOM_DIR:-"custom"}

hashFile="${CUSTOM_DIR}/list.hash"

### Colours ###

if [ -x /usr/bin/tput ] && tput setaf 1 >&/dev/null; then
  c_reset='\033[0m'
  c_white='\033[0;1m'
  c_title='\033[7;1m'
  c_invert='\033[7m'
  c_gray='\033[1;30m'
  c_red='\033[1;31m'
  c_green='\033[1;32m'
  c_yellow='\033[1;33m'
fi

### Functions ###

# printUsage
#   → outputs the help message
function printUsage() {
  echo -e "${c_yellow}Usage${c_reset}
    $(basename $0) [-h|--help]

${c_yellow}Parameters${c_reset}
  -h, --help   display this message

${c_yellow}Overview${c_reset}
  This script analyses a dirty/modified Buildroot tree and builds a 'custom' directory out of it.
  The generated 'custom' directory reproduces the Buildroot tree file hierarchy, but with patches.
  It can then be used by 'mergeToBR.sh' script to reproduce the dirty/modified Buildroot tree from
  a clean/unmodified Buildroot tree (usually, on another developer computer or a CI server).

  Beside the 'custom' directory, this script also generates a specially-crafted 'list.hash' file
  that indicates, for each file modified, if it has been:
    • added to the Buildroot tree
    • removed from the Buildroot tree
    • patched

  See header comments in '${hashSource}' for details about its content.

  This script expects:
    • a valid Buildroot tree (usually a dirty/modified one)

${c_yellow}Environment variables${c_reset}
  BUILDROOT_DIR      indicates the dirty/modified Buildroot tree (default: './buildroot')
  CUSTOM_DIR         indicates where to save the customizations (default: './custom')"
}

# checkPrerequisites
#   → checks pre-requirements and initializes what needs to be
function checkPrerequisites {
  if [[ ! -d ${BUILDROOT_DIR} ]]; then
    echo "Error: BUILDROOT_DIR (${BUILDROOT_DIR}) does not exist or is not a directory."
    exit 1
  fi
  rm -rf "${CUSTOM_DIR}"
  mkdir -p "${CUSTOM_DIR}"
}

# writeHashFileHeader
#   → (over-)writes some documenting header comments to the hashFile
function writeHashFileHeader {
  echo "\
# This is the list of patches to apply to the Buildroot external tree
# First column is either:
#   * a MD5 sum of the file to patch (i.e. the target file)
#   * a line of minus signs ('-') indicates a file that we remove from Buildroot external tree
#   * a line of plus signs ('+') indicates a file that we add to the Buildroot external tree
" > "${hashFile}"
}

# checkStagedChanges
#   → ensures that nothing has been staged (or unmerged) in the Buildroot tree
#     see 'man git-status' for details about its short/porcelain output format.
#     (TL;DR: first character of a line is the index status, second one is the worktree status)
function checkStagedChanges {
  if (cd "${BUILDROOT_DIR}"; git status --porcelain) | grep --silent '^[^? ]'; then
    echo "Error: Buildroot tree (${BUILDROOT_DIR}) has staged or unmerged changes. Exiting."
    exit 1
  fi
}

# listGitChanges [pattern]
#   → list changed files in the Buildroot tree
#     if 'pattern' is specified, it matches the git-status short/porcelain output format
function listGitChanges {
  local pattern=${1:-.*}
  (cd "${BUILDROOT_DIR}"; git status --porcelain) | grep "${pattern}" | cut -c 4-
}

# git [args]
#   → overrides and wraps the 'git' command to isolate it from system-wide settings,
#     because we don't want diffs to be impacted by developer settings (e.g. 'diff.noprefix')
function git {
  GIT_CONFIG_NOSYSTEM=1 GIT_ATTR_NO_SYSTEM=1 HOME=/does/not/exist XDG_CONFIG_HOME=/does/not/exist \
  command git $@
}

### Parameters parsing ###

while [[ -n $1 ]]; do
  case $1 in
    "-h"|"--help"|*)
      printUsage
      exit 64 # EX_USAGE
      ;;
  esac
  shift
done

### MAIN ###

checkPrerequisites
checkStagedChanges
writeHashFileHeader

# Process added files
listGitChanges '^??' | while read -r filePath; do
[ ! -d "$(dirname "${CUSTOM_DIR}/${filePath}")" ] && mkdir -p "$(dirname "${CUSTOM_DIR}/${filePath}")"
  echo -e "${c_green}[added]${c_reset}    ${BUILDROOT_DIR}/${filePath}"
  cp -p "${BUILDROOT_DIR}/${filePath}" "${CUSTOM_DIR}/${filePath}"
  echo "++++++++++++++++++++++++++++++++  ${filePath}" >> "${hashFile}"
  chmod 644 "${CUSTOM_DIR}/${filePath}"
done

# Process removed files
listGitChanges '^ D' | while read -r filePath; do
  echo -e "${c_red}[deleted]${c_reset}  ${BUILDROOT_DIR}/${filePath}"
  echo "--------------------------------  ${filePath}" >> "${hashFile}"
done

# Process modified files
listGitChanges '^ M' | while read -r filePath; do
  echo -e "${c_yellow}[modified]${c_reset} ${BUILDROOT_DIR}/${filePath}"

  modifiedFile="${BUILDROOT_DIR}/${filePath}"
  customFile="${CUSTOM_DIR}/${filePath}"
  patchFile="${customFile}.patch"

  # Create directory in 'custom' tree
  mkdir -p "$(dirname "${customFile}")"
  # Save patch file to 'custom' tree
  (cd "${BUILDROOT_DIR}"; git diff "${filePath}") > "${patchFile}"
  # Save the patched file to 'custom' tree
  cp "$modifiedFile" "$customFile"
  # Reverse-apply the patch to the modified file to obtain the original hash
  patch -p0 --reverse --silent "${modifiedFile}" --input "${patchFile}" --output - | \
    md5sum | \
    sed "s#-\$#${filePath}#" >> "${hashFile}"
  chmod 644 "${patchFile}"
done
