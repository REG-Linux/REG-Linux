#!/bin/bash -e

# PWD = source dir
# BASE_DIR = build dir
# BUILD_DIR = base dir/build
# HOST_DIR = base dir/host
# BINARIES_DIR = images dir
# TARGET_DIR = target dir

##### constants ################
REGLINUX_BINARIES_DIR="${BINARIES_DIR}/reglinux"
GENIMAGE_TMP="${BUILD_DIR}/genimage.tmp"
LOG_DIR="${BUILD_DIR}/post-image-logs"
################################

mkdir -p "${LOG_DIR}"

run_with_log() {
    local label="$1"
    shift
    local log="${LOG_DIR}/${label}.log"

    echo "Running ${label}: $*"
    if "$@" >"${log}" 2>&1; then
        echo "  ${label} succeeded (log at ${log})"
        return 0
    fi

    echo "ERROR: ${label} failed (log follows)"
    cat "${log}"
    exit 1
}

##### find images to build #####
SYSTEM_TARGET=$(grep -E "^BR2_PACKAGE_SYSTEM_TARGET_[A-Z_0-9]*=y$" "${BR2_CONFIG}" | grep -vE "_ANY=" | grep -vE "_GLES[0-9]*=" | sed -e s+'^BR2_PACKAGE_SYSTEM_TARGET_\([A-Z_0-9]*\)=y$'+'\1'+)
REGLINUX_LOWER_TARGET=$(echo "${SYSTEM_TARGET}" | tr '[:upper:]' '[:lower:]')
REGLINUX_IMAGES_TARGETS=$(grep -E "^BR2_TARGET_REGLINUX_IMAGES[ ]*=[ ]*\".*\"[ ]*$" "${BR2_CONFIG}" | sed -e s+"^BR2_TARGET_REGLINUX_IMAGES[ ]*=[ ]*\"\(.*\)\"[ ]*$"+"\1"+)
if test -z "${REGLINUX_IMAGES_TARGETS}"
then
    echo "no BR2_TARGET_REGLINUX_IMAGES defined." >&2
    exit 1
fi
################################

#### common parent dir to al images #
if echo "${REGLINUX_IMAGES_TARGETS}" | grep -qE '^[^ ]*$'
then
    # single board directory
    IMGMODE=single
else
    # when there are several one, the first one is the common directory where to find the create-boot-script.sh directory
    IMGMODE=multi
fi

#### clean the (previous if exists) target directory ###
if test -d "${REGLINUX_BINARIES_DIR}"
then
    rm -rf "${REGLINUX_BINARIES_DIR}" || exit 1
fi
mkdir -p "${REGLINUX_BINARIES_DIR}/images" || exit 1

##### build images #############
SUFFIXVERSION=$(cat "${TARGET_DIR}/usr/share/reglinux/system.version" | sed -e s+'^\([0-9\.]*\).*$'+'\1'+) # xx.yy version
SUFFIXDATE=$(date +%Y%m%d)
VFATUUID="$(date '+%d%m')-$(date '+%M%S')"

#### build the images ###########
TARGET_BOARD_PARENT_PATH="board"
for REGLINUX_PATHSUBTARGET in ${REGLINUX_IMAGES_TARGETS}
do
    REGLINUX_SUBTARGET=$(basename "${REGLINUX_PATHSUBTARGET}")

    #### prepare the boot dir ######
    BOOTNAMEDDIR="${REGLINUX_BINARIES_DIR}/boot_${REGLINUX_SUBTARGET}"
    rm -rf "${BOOTNAMEDDIR}" || exit 1 # remove in case or rerun
    REGLINUX_POST_IMAGE_SCRIPT="${BR2_EXTERNAL_REGLINUX_PATH}/${TARGET_BOARD_PARENT_PATH}/${REGLINUX_PATHSUBTARGET}/create-boot-script.sh"
    run_with_log "create-boot-${REGLINUX_SUBTARGET}" bash "${REGLINUX_POST_IMAGE_SCRIPT}" "${HOST_DIR}" "${BR2_EXTERNAL_REGLINUX_PATH}/${TARGET_BOARD_PARENT_PATH}/${REGLINUX_PATHSUBTARGET}" "${BUILD_DIR}" "${BINARIES_DIR}" "${TARGET_DIR}" "${REGLINUX_BINARIES_DIR}"
    # add some common files
    #nope cp -pr "${BINARIES_DIR}/tools"              "${REGLINUX_BINARIES_DIR}/boot/" || exit 1
    cp     "${BINARIES_DIR}/system-boot.conf" "${REGLINUX_BINARIES_DIR}/boot/" || exit 1
    echo   "${REGLINUX_SUBTARGET}" > "${REGLINUX_BINARIES_DIR}/boot/boot/system.board" || exit 1

    #### boot-$BOARD.tar.zst ###############
    echo "creating images/${REGLINUX_SUBTARGET}/boot-${REGLINUX_SUBTARGET}.tar.zst"
    mkdir -p "${REGLINUX_BINARIES_DIR}/images/${REGLINUX_SUBTARGET}" || exit 1
    (cd "${REGLINUX_BINARIES_DIR}/boot" && tar -I "zstd" -cf "${REGLINUX_BINARIES_DIR}/images/${REGLINUX_SUBTARGET}/boot-${REGLINUX_SUBTARGET}.tar.zst" *) || exit 1

    # create *.img
    if [ "${REGLINUX_LOWER_TARGET}" = "${REGLINUX_SUBTARGET}" ]; then
        BATOCERAIMG="${REGLINUX_BINARIES_DIR}/images/${REGLINUX_SUBTARGET}/reglinux-${REGLINUX_SUBTARGET}-${SUFFIXVERSION}-${SUFFIXDATE}.img"
    else
        BATOCERAIMG="${REGLINUX_BINARIES_DIR}/images/${REGLINUX_SUBTARGET}/reglinux-${REGLINUX_LOWER_TARGET}-${REGLINUX_SUBTARGET}-${SUFFIXVERSION}-${SUFFIXDATE}.img"
    fi
    echo "creating images/${REGLINUX_SUBTARGET}/"$(basename "${BATOCERAIMG}")"..." >&2
    rm -rf "${GENIMAGE_TMP}" || exit 1
    GENIMAGEDIR="${BR2_EXTERNAL_REGLINUX_PATH}/${TARGET_BOARD_PARENT_PATH}/${REGLINUX_PATHSUBTARGET}"
    GENIMAGEFILE="${GENIMAGEDIR}/genimage.cfg"
    FILES=$(find "${REGLINUX_BINARIES_DIR}/boot" -type f | sed -e s+"^${REGLINUX_BINARIES_DIR}/boot/\(.*\)$"+"file \1 \{ image = '\1' }"+ | tr '\n' '@')
    cat "${GENIMAGEFILE}" | sed -e s+'@files'+"${FILES}"+ | tr '@' '\n' > "${REGLINUX_BINARIES_DIR}/genimage.cfg" || exit 1
	# Include the UUID of boot partition in extraargs
	sed -i "s/ -n REGLINUX/ -n REGLINUX -i ${VFATUUID//-}/g" "${REGLINUX_BINARIES_DIR}/genimage.cfg" || exit 1
	# Change "label=REGLINUX" to "uuid= ..." in boot files
	find "${REGLINUX_BINARIES_DIR}/boot/" -type f \( -iname "LinuxLoader.cfg" -o -iname "extlinux.conf" -o -iname "cmdline.txt" -o -iname "boot.ini" -o -iname "uEnv.txt" -o -iname "syslinux.cfg" -o -iname "grub.cfg" \) -exec sed -i "s/label=REGLINUX/uuid=$VFATUUID/g" {} \+

    # install syslinux
    if grep -qE "^BR2_TARGET_SYSLINUX=y$" "${BR2_CONFIG}"
    then
		GENIMAGEBOOTFILE="${GENIMAGEDIR}/genimage-boot.cfg"
		echo "installing syslinux" >&2
		cat "${GENIMAGEBOOTFILE}" | sed -e s+'@files'+"${FILES}"+ | tr '@' '\n' > "${REGLINUX_BINARIES_DIR}/genimage-boot.cfg" || exit 1
		# Include the UUID of boot partition in extraargs
		sed -i "s/ -n REGLINUX/ -n REGLINUX -i ${VFATUUID//-}/g" "${REGLINUX_BINARIES_DIR}/genimage-boot.cfg" || exit 1
		run_with_log "genimage-boot-${REGLINUX_SUBTARGET}" "${HOST_DIR}/bin/genimage" --rootpath="${TARGET_DIR}" --inputpath="${REGLINUX_BINARIES_DIR}/boot" --outputpath="${REGLINUX_BINARIES_DIR}" --config="${REGLINUX_BINARIES_DIR}/genimage-boot.cfg" --tmppath="${GENIMAGE_TMP}"
		"${HOST_DIR}/bin/syslinux" -i "${REGLINUX_BINARIES_DIR}/boot.vfat" -d "/boot/syslinux" || exit 1
		# remove genimage temp path as sometimes genimage v14 fails to start
		rm -rf ${GENIMAGE_TMP}
		mkdir ${GENIMAGE_TMP}
    fi
    ###
    run_with_log "genimage-${REGLINUX_SUBTARGET}" "${HOST_DIR}/bin/genimage" --rootpath="${TARGET_DIR}" --inputpath="${REGLINUX_BINARIES_DIR}/boot" --outputpath="${REGLINUX_BINARIES_DIR}" --config="${REGLINUX_BINARIES_DIR}/genimage.cfg" --tmppath="${GENIMAGE_TMP}"

    rm -f "${REGLINUX_BINARIES_DIR}/boot.vfat" || exit 1
    rm -f "${REGLINUX_BINARIES_DIR}/userdata.ext4" || exit 1
    mv "${REGLINUX_BINARIES_DIR}/reglinux.img" "${BATOCERAIMG}" || exit 1
    "${HOST_DIR}/usr/bin/pigz" -1 -p 4 "${BATOCERAIMG}" || exit 1

    # delete the boot
    rm -rf "${REGLINUX_BINARIES_DIR}/boot" || exit 1

    # copy the version file needed for version check
    cp "${TARGET_DIR}/usr/share/reglinux/system.version" "${REGLINUX_BINARIES_DIR}/images/${REGLINUX_SUBTARGET}" || exit 1
done

#### md5 and sha256 #######################
for REGLINUX_PATHSUBTARGET in ${REGLINUX_IMAGES_TARGETS}
do
    REGLINUX_SUBTARGET=$(basename "${REGLINUX_PATHSUBTARGET}")
    if [ "${REGLINUX_LOWER_TARGET}" = "${REGLINUX_SUBTARGET}" ]; then
        REGLINUX_SUBTARGET="${REGLINUX_LOWER_TARGET}"
    fi
    for FILE in "${REGLINUX_BINARIES_DIR}/images/${REGLINUX_SUBTARGET}/boot-${REGLINUX_SUBTARGET}.tar.zst" "${REGLINUX_BINARIES_DIR}/images/${REGLINUX_SUBTARGET}/reglinux-"*".img.gz"
    do
        echo "creating ${FILE}.md5"
        CKS=$(md5sum "${FILE}" | sed -e s+'^\([^ ]*\) .*$'+'\1'+)
        echo "${CKS}" > "${FILE}.md5"
        echo "${CKS}  $(basename "${FILE}")" >> "${REGLINUX_BINARIES_DIR}/MD5SUMS"
        echo "creating ${FILE}.sha256"
        CKS=$(sha256sum "${FILE}" | sed -e s+'^\([^ ]*\) .*$'+'\1'+)
        echo "${CKS}" > "${FILE}.sha256"
        echo "${CKS}  $(basename "${FILE}")" >> "${REGLINUX_BINARIES_DIR}/SHA256SUMS"
    done
done

# Remove lingering GENIMAGE_TMP directory from build after last image
rm -rf ${GENIMAGE_TMP}

#### update the target dir with some information files
cp "${TARGET_DIR}/usr/share/reglinux/system.version" "${REGLINUX_BINARIES_DIR}" || exit 1
"${BR2_EXTERNAL_REGLINUX_PATH}"/scripts/linux/systemsReport.sh "${PWD}" "${REGLINUX_BINARIES_DIR}" || exit 1
