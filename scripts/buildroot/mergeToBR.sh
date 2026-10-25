#!/bin/bash
# Credits: Recalbox Team

### Global variables ###

BUILDROOT_DIR=${BUILDROOT_DIR:-"./buildroot"}
CUSTOM_DIR=${CUSTOM_DIR:-"./custom"}
hashFile="${CUSTOM_DIR}/list.hash"

### Colours ###

if [ -x /usr/bin/tput ] && tput setaf 1 >&/dev/null; then
  c_reset='\033[0m'
  c_white='\033[0;1m'
  c_title='\033[7;1m'
  c_invert='\033[7m'
  c_gray='\033[1;30m'
  c_red='\033[1;31m'
  c_bg_red='\033[41;1m'
  c_green='\033[1;32m'
  c_yellow='\033[1;33m'
fi

[[ -z $BUILDROOT_DIR && ! -d ./buildroot ]] && echo "You must set the env var BUILDROOT_DIR to the location of the buildroot dir to use this script" && exit 1
[[ -z $BUILDROOT_DIR && -d ./buildroot ]] && BUILDROOT_DIR="./buildroot"

declare -x foundError

### Functions ###

# printUsage
#   → outputs the help message
function printUsage() {
  echo -e "${c_yellow}Usage${c_reset}
    $(basename "$0") [-c|--check-only] [-f|--force] [-u|--update-md5] [-h|--help]

${c_yellow}Parameters${c_reset}
  -c, --check-only   check that changes can be applied, but don't actually apply them
  -f, --force        apply changes, even if not all of them can be applied
  -u, --update-md5   update MD5 hashes in the list.hash file when target files differ
  -h, --help         display this message

${c_yellow}Overview${c_reset}
  This script applies customizations to a (usually clean/unmodified) Buildroot tree.

  It reads a specially-crafted file named 'list.hash' that indicates, for each file, if we want to:
    • add it to the Buildroot tree
    • remove it from the Buildroot tree
    • patch it

  This 'list.hash' file can be automatically generated from a dirty/modified Buildroot tree by
  the 'generateCustom.sh' script. It can also be written manually, in which case, see header
  comments in '${hashFile}' for details about its content.

  This script expects:
    • a valid Buildroot tree
    • a directory that reproduces the Buildroot tree file hierarchy, but with patch files instead
    • a 'list.hash' file to list changes to apply

${c_yellow}Environment variables${c_reset}
  BUILDROOT_DIR      indicates the Buildroot tree (default: './buildroot')
  CUSTOM_DIR         indicates where the customizations are (default: './custom')"
}

# printError <message>
#   → output helper
function printError() {
  local readonly message=$1
  echo -e "${c_red}[error]${c_reset} ${message}"
}

# printIgnore <message>
#   → output helper
function printIgnore() {
  local readonly message=$1
  echo -e "${c_gray}[ignore]${c_reset} ${message}"
}

# printWarning <message>
#   → output helper
function printWarning() {
  local readonly message=$1
  echo -e "${c_yellow}[warning]${c_reset} ${message}"
}

# printSuccess <message>
#   → output helper
function printSuccess() {
  local readonly message=$1
  echo -e "${c_green}[success]${c_reset} ${message}"
}

# printTitle <message>
#   → output helper
function printTitle() {
  local -r message=$1
  echo -e "${c_invert}>>> $(basename "${BASH_SOURCE[0]}" .sh) ${c_title}${message}${c_reset}"
}

# hasExpectedChecksum <file> <hash>
#   → is success if <file> MD5 checksum is <hash>
function hasExpectedChecksum() {
  local -r file=$1
  local -r hash=$2
  echo "${hash} ${BUILDROOT_DIR}/${file}" | md5sum --status --check
}

# isFileIdentical <file>
#   → is success if <file> is identical in ${CUSTOM_DIR} and in ${BUILDROOT_DIR}
function isFileIdentical() {
  local readonly file=$1
  diff -qN {"${CUSTOM_DIR}","${BUILDROOT_DIR}"}/"${file}" > /dev/null
}

# checkFileToAdd <file>
#   → checks if <file> exists in custom tree and that a different one does not exist in Buildroot tree
function checkFileToAdd() {
  local readonly file=$1

  if [[ ! -f ${CUSTOM_DIR}/${file} ]]; then
    foundError=1
    printError "${c_white}${file}${c_reset} source file does not exist"
  elif isFileIdentical "${file}"; then
    printIgnore "${c_white}${file}${c_reset} already added"
  elif [[ -f ${BUILDROOT_DIR}/${file} ]]; then
    foundError=1
    printError "${c_white}${file}${c_reset} target file already exists and is different than source file"
  else
    filesToAdd+=("${file}")
    printSuccess "${c_white}${file}${c_reset} can be added"
  fi
}

# checkFileToRemove <file>
#   → check that <file> exists in Buildroot tree and that it has not already been removed
function checkFileToRemove() {
  local -r file=$1

  if [[ ! -f ${BUILDROOT_DIR}/${file} ]]; then
    if (cd "${BUILDROOT_DIR}"; git status --porcelain "${file}" | grep --silent "^ D "); then
      printIgnore "${c_white}${file}${c_reset} already removed"
    else
      foundError=1
      printError "${c_white}${file}${c_reset} file to remove does not exist"
    fi
  else
    filesToRemove+=("${file}")
    printSuccess "${c_white}${file}${c_reset} can be removed"
  fi
}

# checkFileToPatch <file> <hash>
#   → checks that <file> exists in both custom and Buildroot trees, and that patch applies
function checkFileToPatch() {
  local -r file=$1
  local -r hash=$2

  if [[ ! -f ${CUSTOM_DIR}/${file} || ! -f ${BUILDROOT_DIR}/${file} ]]; then
    foundError=1
    [[ ! -f ${CUSTOM_DIR}/${file} ]] && printError "${c_white}${file}${c_reset} source file doesn't exist"
    [[ ! -f ${BUILDROOT_DIR}/${file} ]] && printError "${c_white}${file}${c_reset} target file doesn't exist"
  elif isFileIdentical "${file}"; then
    printIgnore "${c_white}${file}${c_reset} already patched"
  elif ! hasExpectedChecksum "${file}" "${hash}"; then
    if [[ ${optionUpdateMd5} = 1 ]]; then
      # Get the current MD5 hash of the target file
      current_hash=$(md5sum "${BUILDROOT_DIR}/${file}" | cut -d' ' -f1)
      printWarning "${c_white}${file}${c_reset} target file does not have expected MD5 checksum, updating hash from ${hash} to ${current_hash}"
      updateHashInFile "${file}" "${current_hash}"

      # Let's try to apply the patch after updating the hash
      if ! patch --dry-run --silent -p0 "${BUILDROOT_DIR}/${file}" < "${CUSTOM_DIR}/${file}.patch" > /dev/null; then
        foundError=1
        printError "${c_white}${file}${c_reset} patch fails to apply even after hash update"
      else
        filesToPatch+=("${file}")
        printSuccess "${c_white}${file}${c_reset} can be patched (hash updated)"
      fi
    else
      foundError=1
      printError "${c_white}${file}${c_reset} target file does not have expected MD5 checksum"
    fi
  else
    # Let's try to apply the patch
    if ! patch --dry-run --silent -p0 "${BUILDROOT_DIR}/${file}" < "${CUSTOM_DIR}/${file}.patch" > /dev/null; then
      foundError=1
      printError "${c_white}${file}${c_reset} patch fails to apply"
    else
      filesToPatch+=("${file}")
      printSuccess "${c_white}${file}${c_reset} can be patched"
    fi
  fi
}

# addFiles
#   → apply file additions to Buildroot tree
function addFiles() {
  if [[ -z ${filesToAdd[0]} ]]; then
    echo -e "${c_white}No file to add.${c_reset} Skipping."
  else
    echo -e "${c_white}Adding files…${c_reset}"
    for fileToAdd in "${filesToAdd[@]}"; do
      # shellcheck disable=SC2015
      install -D {"${CUSTOM_DIR}","${BUILDROOT_DIR}"}/"${fileToAdd}" \
        && printSuccess "${fileToAdd}" \
        || { printError "${fileToAdd}"; return 1; }
    done
  fi
}

# removeFiles
#   → apply file deletions to Buildroot tree
function removeFiles() {
  if [[ -z ${filesToRemove[0]} ]]; then
    echo -e "${c_white}No file to remove.${c_reset} Skipping."
  else
    echo -e "${c_white}Removing files…${c_reset}"
    for fileToRemove in "${filesToRemove[@]}"; do
      # shellcheck disable=SC2015
      rm "${BUILDROOT_DIR}/${fileToRemove}" \
        && printSuccess "${fileToRemove}" \
        || { printError "${fileToRemove}"; return 1; }
    done
  fi
}

# updateHashInFile <file> <new_hash>
#   → updates the hash for a specific file in the hashFile
function updateHashInFile() {
  local -r file=$1
  local -r new_hash=$2
  local temp_hash_file="${hashFile}.tmp"

  # Create temporary file with updated hash
  while IFS= read -r line; do
    if [[ -n "$line" && ! "$line" =~ ^# ]]; then
      # Extract the hash (first 32 characters before first space) and filename (after "  ")
      if [[ "$line" =~ ^[a-fA-F0-9]{32}\ \ .*$ ]]; then
        # This is a line with an MD5 hash, extract the filename part after "  "
        local line_hash=$(echo "$line" | cut -d' ' -f1)
        local line_file=$(echo "$line" | cut -d' ' -f3-)

        if [[ "${line_file}" == "${file}" ]]; then
          # This is the line with the hash for our file, update it
          echo "${new_hash}  ${file}"
        else
          # Keep the original line
          echo "${line}"
        fi
      else
        # Not a hash line, keep it as is
        echo "${line}"
      fi
    else
      # Comment or empty line, keep it as is
      echo "${line}"
    fi
  done < "${hashFile}" > "${temp_hash_file}"

  # Replace the original file with the updated one
  mv "${temp_hash_file}" "${hashFile}"
}

# applyPatches
#   → actually apply patches to Buildroot tree
function applyPatches() {
  if [[ -z ${filesToPatch[0]} ]]; then
    echo -e "${c_white}No patch to apply.${c_reset} Skipping."
  else
    echo -e "${c_white}Applying patches…${c_reset}"
    for fileToPatch in "${filesToPatch[@]}"; do
      patchFile="${fileToPatch}.patch"
      # shellcheck disable=SC2015
      patch --silent -p0 "${BUILDROOT_DIR}/${fileToPatch}" < "${CUSTOM_DIR}/${patchFile}"  \
        && printSuccess "${fileToPatch}" \
        || { printError "${fileToPatch}"; return 1; }
    done
  fi
}

### Parameters parsing ###

while [[ -n $1 ]]; do
  case $1 in
    "-f"|"--force")
      optionForce=1
      ;;
    "-c"|"--check-only")
      optionCheckOnly=1
      ;;
    "-u"|"--update-md5")
      optionUpdateMd5=1
      ;;
    "-h"|"--help"|*)
      printUsage
      exit 64 # EX_USAGE
      ;;
  esac
  shift
done

### Step 1: Basic checks (environment, prerequisites) ###

printTitle "1. Check environment"

# Check that ${hashFile} exist
# shellcheck disable=SC2015
[[ -f ${hashFile} ]] \
  && printSuccess "${c_white}${hashFile}${c_reset} is present" \
  || { printError "${c_white}${hashFile}${c_reset} is missing"; exit 1; }

# Check that ${hashFile} is exhaustive
for file in $(find "${CUSTOM_DIR}" -type f | grep -v "^${hashFile}$" | grep -v '.patch$'); do
  file=${file/${CUSTOM_DIR}\//}
  if ! grep -q "${file}$" "${hashFile}"; then
    printWarning "${c_white}${file}${c_reset} exists in custom tree, but is not listed in '${hashFile}'. It might be a mistake."
  fi
done

# Check that Buildroot tree exists
# shellcheck disable=SC2015
[[ -d ${BUILDROOT_DIR} && -d ${BUILDROOT_DIR}/package ]] \
  && printSuccess "${c_white}${BUILDROOT_DIR}${c_reset} is a valid Buildroot tree" \
  || { printError "${c_white}${BUILDROOT_DIR}${c_reset} is not a valid Buildroot tree"; exit 1; }

### Step 2: Check that patches can be applied

printTitle "2. Check that changes can be applied"

# we use file descriptor 3 here, to not mess with stdin, stdout, stderr, …
# we cannot use a pipe here, otherwise all variables defined above are empty when the loop exits
while read -u 3 -r line; do
  hash=$(echo "${line}" | cut -d ' ' -f 1)
  file=$(echo "${line}" | cut -d ' ' -f 3)

  if [[ ${hash} == "--------------------------------" ]] ; then
    checkFileToRemove "${file}"
  elif [[ ${hash} == "++++++++++++++++++++++++++++++++" ]] ; then
    checkFileToAdd "${file}"
  else
    if [[ ! ${hash} =~ [[:alnum:]]{32} ]]; then
      foundError=1
      printError "${c_white}${file}${c_reset} hash is not a MD5 sum"
    else
      checkFileToPatch "${file}" "${hash}"
    fi
  fi
done 3< <(grep -Ev '(^ *$|^#)' "${hashFile}")

# If update MD5 option is enabled and no errors found, we might want to update all hashes
if [[ ${optionUpdateMd5} = 1 ]]; then
  printTitle "2b. Updating MD5 hashes if needed"

  # Process the hash file again to check for any files that could have updated hashes
  while read -u 4 -r line; do
    hash=$(echo "${line}" | cut -d ' ' -f 1)
    file=$(echo "${line}" | cut -d ' ' -f 3)

    if [[ "${hash}" != "--------------------------------" ]] && [[ "${hash}" != "++++++++++++++++++++++++++++++++" ]] && [[ ${hash} =~ [[:alnum:]]{32} ]]; then
      # This is a file with an MD5 hash, check if the current file has a different hash
      if [[ -f ${BUILDROOT_DIR}/${file} ]]; then
        current_hash=$(md5sum "${BUILDROOT_DIR}/${file}" | cut -d' ' -f1)
        if [[ "${hash}" != "${current_hash}" ]]; then
          printWarning "${c_white}${file}${c_reset} has different hash, updating from ${hash} to ${current_hash}"
          updateHashInFile "${file}" "${current_hash}"
        fi
      fi
    fi
  done 4< <(grep -Ev '(^ *$|^#)' "${hashFile}")
fi

if [[ ${optionCheckOnly} = 1 ]]; then
  exit ${foundError}
fi

if [[ ${foundError} = 1 ]] ; then
  if [[ ${optionForce} = 1 ]]; then
    printWarning "Errors were found during the dry run. Only valid modifications will be applied below."
  else
    printTitle "${c_bg_red}🚫 Aborting"
    echo "Some errors were found. Cannot patch Buildroot tree. Aborting." >&2
    echo "No actions have been done, '${BUILDROOT_DIR}' is still neat and clean" >&2
    exit 1
  fi
fi

printTitle "3. Apply changes to Buildroot tree"

addFiles && removeFiles && applyPatches

exit ${foundError}
