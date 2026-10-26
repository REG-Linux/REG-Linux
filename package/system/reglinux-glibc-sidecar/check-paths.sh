#!/bin/bash
#
# check-paths.sh <sidecar root> <prefix>
#
# Lists the absolute paths outside <prefix> that the sidecar's ELF files
# reference, and fails if one is a directory the musl system loads code from:
# a glibc program would then dlopen() a musl plugin and crash.
#
# FAIL  a known plugin/driver directory, or (with REG_MUSL_FILELIST, a file
#       listing a musl image's files, one absolute path per line) any
#       referenced directory that holds shared objects in that image
# info  everything else (data files, /etc config, compiled-in defaults that
#       don't exist on the boards, such as RUNPATHs into /usr/lib/<dir>)
#
set -euo pipefail

ROOT="$1"
PREFIX="$2"

# Directories the musl boards (or common packages) load code from
PLUGIN_DIRS='^/(usr/)?lib(64)?/(dri|gbm|alsa-lib|spa-[0-9.]+|pipewire-[0-9.]+|gio/modules|gstreamer-1\.0|vdpau|ossl-modules|engines-[0-9]+|libdecor|sasl2|pkcs11|jack|gdk-pixbuf-2\.0|gtk-[0-9.]+)(/|$)|^/(usr/share|etc)/(vulkan|glvnd)(/|$)'

declare -A seen
fail=0

while IFS= read -r -d '' f; do
	head -c4 "${f}" 2>/dev/null | grep -q 'ELF' || continue
	rel="${f#"${ROOT}"/}"
	while IFS= read -r p; do
		[[ "${p}" == "${PREFIX}"* ]] && continue
		key="${p}|${rel}"
		[ -n "${seen[${key}]:-}" ] && continue
		seen[${key}]=1
		status=info
		if [[ "${p}" =~ ${PLUGIN_DIRS} ]]; then
			status=FAIL
		elif [ -n "${REG_MUSL_FILELIST:-}" ] && [ -f "${REG_MUSL_FILELIST}" ] &&
			grep -qE "^${p%/}/[^/]+\.so(\.|$)" "${REG_MUSL_FILELIST}"; then
			status=FAIL
		fi
		line=$(printf '%-4s %s  (%s)' "${status}" "${p}" "${rel}")
		echo "${line}"
		# stdout is the report file: failures also go to the build log
		if [ "${status}" = FAIL ]; then fail=1; echo "${line}" >&2; fi
	# whole path tokens first (so /usr/glibc/lib/x isn't read as /lib/x), then
	# keep the system locations
	done < <(grep -aoE '(/[A-Za-z0-9_.+@-]+){2,}' "${f}" |
		grep -E '^/(usr/(lib|lib64|libexec|share)|lib|lib64|etc|usr/glibc[0-9]*)/' | sort -u)
done < <(find "${ROOT}" -type f -print0)

if [ "${fail}" = 1 ]; then
	echo "check-paths: the sidecar references musl plugin directories (FAIL lines above)" >&2
	exit 1
fi
