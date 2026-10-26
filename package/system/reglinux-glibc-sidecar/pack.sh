#!/bin/bash
#
# Post-image script of the reglinux-glibc-sidecar-<arch> configs.
#
# Builds $BINARIES_DIR/glibc-<arch>.squashfs (+ .md5), whose content musl
# boards mount on /usr/glibc (armhf: /usr/glibc32, the glibc-sidecar prefix):
#   lib/    relocated glibc + every other shared library, flat (the loader's
#           only search dir), plus plugin subdirs (dri/, gbm/, alsa-lib/, ...)
#   share/  data installed under the prefix (alsa) + Vulkan ICDs
#   etc/    ld.so.conf, asound.conf, alsa conf.d
#   VERSION REG version the sidecar was built with
# then refuses the result if a library still points at a plugin directory of
# the musl system (check-paths.sh).
#
set -euo pipefail

BINARIES_DIR="$1"
PKGDIR="$(dirname "$(readlink -f "$0")")"
if grep -q '^BR2_aarch64=y' "${BR2_CONFIG}"; then
	ARCH=aarch64; P=/usr/glibc
else
	ARCH=armhf; P=/usr/glibc32
fi
NAME="glibc-${ARCH}"
ROOT="${BUILD_DIR}/${NAME}-root"

# glibc's own libraries: the relocated build in ${TARGET_DIR}${P} is the one
# to ship; the toolchain copies in /lib are only what the build linked against
GLIBC_OWN='^(ld-linux.*|libc\.so.*|libm\.so.*|libmvec\.so.*|libpthread\.so.*|libdl\.so.*|librt\.so.*|libresolv\.so.*|libutil\.so.*|libanl\.so.*|libnss_.*|libthread_db\.so.*|libBrokenLocale\.so.*|libc_malloc_debug\.so.*|libmemusage\.so|libpcprofile\.so)$'
# Build-time only: REG's Mesa needs clang/LLVM to precompile its OpenCL-C
# kernels (mesa_clc), not at runtime (no llvmpipe). Not SPIRV-Tools: libgallium
# and the Vulkan drivers link it. Step 7 catches anything excluded by mistake.
BUILD_ONLY='^(libLLVM.*|libclang.*|libclc.*|libLTO\.so.*|libRemarks\.so.*|libLLVMSPIRVLib\.so.*)$'
# Not libraries: build metadata, interpreters' modules, systemd/udev bits
# gconv: the toolchain's full set (BR2_TOOLCHAIN_GLIBC_GCONV_LIBS_COPY); glibc-sidecar
# ships its own subset in lib/gconv
# pulseaudio: the daemon's libs and modules (no daemon here); its client's
# private lib is put flat in lib/ below
SKIP_SUBDIRS='^(pkgconfig|cmake|gcc|python.*|perl.*|lua|girepository-.*|locale|gconv|pulseaudio|udev|systemd|sysctl\.d|tmpfiles\.d|modules-load\.d|debug)$'

rm -rf "${ROOT}"
mkdir -p "${ROOT}/lib" "${ROOT}/share" "${ROOT}/etc"

# 1. Everything installed under the prefix: relocated glibc, relocated
#    plugins and config (dri/, alsa-lib/, share/alsa, etc/asound.conf, VERSION)
cp -a "${TARGET_DIR}${P}/." "${ROOT}/"

# 2. Every other shared library, flattened into lib/
for d in "${TARGET_DIR}/lib" "${TARGET_DIR}/usr/lib"; do
	find "${d}" -maxdepth 1 \( -type f -o -type l \) -name '*.so*' -print0 |
	while IFS= read -r -d '' f; do
		b="${f##*/}"
		[[ "${b}" =~ ${GLIBC_OWN} ]] && continue
		[[ "${b}" =~ ${BUILD_ONLY} ]] && continue
		[ -e "${ROOT}/lib/${b}" ] || [ -L "${ROOT}/lib/${b}" ] && continue
		cp -a "${f}" "${ROOT}/lib/"
	done
done

# 3. Library subdirs (plugins, private libs) keep their layout under lib/.
#    Private libs reached through a RUNPATH into /usr/lib/<dir> (libpulse ->
#    pulseaudio/libpulsecommon) are also put flat in lib/: that RUNPATH
#    doesn't exist on the device, so the loader falls back to lib/.
find "${TARGET_DIR}/usr/lib" -mindepth 1 -maxdepth 1 -type d -print0 |
while IFS= read -r -d '' sub; do
	s="${sub##*/}"
	[[ "${s}" =~ ${SKIP_SUBDIRS} ]] && continue
	find "${sub}" -name '*.so*' -print -quit | grep -q . || continue
	mkdir -p "${ROOT}/lib/${s}"
	cp -a --update=none "${sub}/." "${ROOT}/lib/${s}/"
done
# libpulse's private lib (step 2 copied an absolute link to it)
for f in "${TARGET_DIR}/usr/lib/pulseaudio/"libpulsecommon-*.so; do
	[ -e "${f}" ] || continue
	rm -f "${ROOT}/lib/${f##*/}"
	cp -a "${f}" "${ROOT}/lib/"
done

# 3b. Absolute symlinks would resolve into the musl system once mounted:
#     re-point them inside lib/, or drop them when the target isn't shipped
#     (step 7 then reports anything that needed it)
find "${ROOT}/lib" -type l -lname '/*' -print0 |
while IFS= read -r -d '' l; do
	t="$(readlink "${l}")"
	rm -f "${l}"
	if [ "${t##*/}" != "${l##*/}" ] && [ -e "${ROOT}/lib/${t##*/}" ]; then
		ln -s "${t##*/}" "${l}"
	fi
done

# 3c. RUNPATH/RPATH entries outside the prefix are searched before lib/, so
#     they'd load the musl system's copy of a library (libpulse's
#     /usr/lib/pulseaudio did). Keep only entries under the prefix.
while IFS= read -r -d '' f; do
	head -c4 "${f}" 2>/dev/null | grep -q 'ELF' || continue
	rp="$("${HOST_DIR}/bin/patchelf" --print-rpath "${f}" 2>/dev/null)" || continue
	[ -n "${rp}" ] || continue
	keep="$(echo "${rp}" | tr ':' '\n' | grep -E "^${P}(/|$)" | paste -sd: -)" || true
	if [ "${keep}" != "${rp}" ]; then
		if [ -n "${keep}" ]; then
			"${HOST_DIR}/bin/patchelf" --set-rpath "${keep}" "${f}"
		else
			"${HOST_DIR}/bin/patchelf" --remove-rpath "${f}"
		fi
	fi
done < <(find "${ROOT}" -type f -print0)

# 4. Vulkan ICDs: Mesa writes absolute /usr/lib/... library paths; a bare file
#    name makes the loader dlopen() it from the sidecar's own lib/
if [ -d "${TARGET_DIR}/usr/share/vulkan/icd.d" ]; then
	mkdir -p "${ROOT}/share/vulkan/icd.d"
	for j in "${TARGET_DIR}/usr/share/vulkan/icd.d/"*.json; do
		[ -e "${j}" ] || continue
		sed -E 's#("library_path"[[:space:]]*:[[:space:]]*")[^"]*/([^"/]+")#\1\2#' "${j}" \
			> "${ROOT}/share/vulkan/icd.d/${j##*/}"
	done
fi

# 4b. alsa.conf hard-codes /etc and ~ for the user config: read the sidecar's
#     own conf.d and asound.conf instead (the musl system's select PipeWire's
#     ALSA plugin, which the sidecar doesn't have)
if [ -f "${ROOT}/share/alsa/alsa.conf" ]; then
	sed -i -e '/"\/var\/lib\/alsa\/conf.d"/d; /"\/usr\/etc\/alsa\/conf.d"/d; /"~\/.asoundrc"/d' \
		-e "s|\"/etc/alsa/conf.d\"|\"${P}/etc/alsa/conf.d\"|" \
		-e "s#\"/etc/asound.conf|||/usr/etc/asound.conf\"#\"${P}/etc/asound.conf\"#" \
		"${ROOT}/share/alsa/alsa.conf"
	grep -q "\"${P}/etc/asound.conf\"" "${ROOT}/share/alsa/alsa.conf" ||
		{ echo "pack: alsa.conf: could not point it at ${P}/etc" >&2; exit 1; }
fi

# 4c. Mesa's libEGL references wl_fixes_interface (wayland >= 1.24); make it
#     NEED the compat library defining it, for when an older libwayland-client
#     is loaded first (PortMaster's Weston pack bundles one)
egl="$(readlink -f "${ROOT}/lib/libEGL.so.1" 2>/dev/null || true)"
if [ -f "${egl}" ] && [ -f "${ROOT}/lib/libwayland-fixes-compat.so" ] &&
	! readelf -d "${egl}" | grep -q 'libwayland-fixes-compat.so'; then
	"${HOST_DIR}/bin/patchelf" --add-needed libwayland-fixes-compat.so "${egl}"
fi

# 5. Unversioned GL names: some ports were linked against them directly
for l in libEGL.so.1 libGLESv2.so.2 libGLESv1_CM.so.1; do
	if [ -e "${ROOT}/lib/${l}" ] && [ ! -e "${ROOT}/lib/${l%.*}" ]; then
		ln -s "${l}" "${ROOT}/lib/${l%.*}"
	fi
done

# 6. No headers, static libs or libtool files in a runtime image
find "${ROOT}" \( -name '*.a' -o -name '*.la' -o -name '*.h' \) -delete
rm -rf "${ROOT}/include"

# 7. Refuse a sidecar that can't load: every library an ELF in it NEEDs must be
#    in lib/ (glibc's own included) or in one of its RUNPATHs under the prefix.
#    A musl-linked library fails here too: it NEEDs libc.so, which isn't shipped.
missing=0
while IFS= read -r -d '' f; do
	head -c4 "${f}" 2>/dev/null | grep -q 'ELF' || continue
	dirs="${ROOT}/lib"
	for r in $(readelf -d "${f}" 2>/dev/null | sed -n 's/.*(R\(UN\)\{0,1\}PATH).*\[\(.*\)\]/\2/p' | tr ':' ' '); do
		case "${r}" in
			"${P}"/*) dirs="${dirs} ${ROOT}${r#"${P}"}" ;;
			*) echo "pack: ${f#"${ROOT}"/} keeps RUNPATH ${r}, outside ${P}" >&2; missing=1 ;;
		esac
	done
	for n in $(readelf -d "${f}" 2>/dev/null | sed -n 's/.*(NEEDED).*\[\(.*\)\]/\1/p'); do
		found=0
		for d in ${dirs}; do [ -e "${d}/${n}" ] && found=1 && break; done
		if [ "${found}" = 0 ]; then
			echo "pack: ${f#"${ROOT}"/} needs ${n}, not in the sidecar" >&2
			missing=1
		fi
	done
done < <(find "${ROOT}" -type f -print0)
[ "${missing}" = 0 ] || { echo "pack: missing libraries (above)" >&2; exit 1; }

# 8. Refuse a sidecar that would load a musl plugin
"${PKGDIR}/check-paths.sh" "${ROOT}" "${P}" > "${BINARIES_DIR}/${NAME}.paths.txt"

# 9. The image
rm -f "${BINARIES_DIR}/${NAME}.squashfs"
"${HOST_DIR}/bin/mksquashfs" "${ROOT}" "${BINARIES_DIR}/${NAME}.squashfs" \
	-noappend -all-root -comp zstd -quiet
(cd "${BINARIES_DIR}" && md5sum "${NAME}.squashfs" > "${NAME}.squashfs.md5")
cp "${ROOT}/VERSION" "${BINARIES_DIR}/${NAME}.VERSION"

echo "${NAME}: $(du -sh "${ROOT}" | cut -f1) unpacked, $(du -h "${BINARIES_DIR}/${NAME}.squashfs" | cut -f1) squashfs, $(find "${ROOT}/lib" -maxdepth 1 -name '*.so*' | wc -l) library files"
