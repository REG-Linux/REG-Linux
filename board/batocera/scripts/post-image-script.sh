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
################################

##### find images to build #####
BATOCERA_TARGET=$(grep -E "^BR2_PACKAGE_BATOCERA_TARGET_[A-Z_0-9]*=y$" "${BR2_CONFIG}" | grep -vE "_ANY=" | grep -vE "_GLES[0-9]*=" | sed -e s+'^BR2_PACKAGE_BATOCERA_TARGET_\([A-Z_0-9]*\)=y$'+'\1'+)
BATOCERA_LOWER_TARGET=$(echo "${BATOCERA_TARGET}" | tr '[:upper:]' '[:lower:]')
BATOCERA_IMAGES_TARGETS=$(grep -E "^BR2_TARGET_BATOCERA_IMAGES[ ]*=[ ]*\".*\"[ ]*$" "${BR2_CONFIG}" | sed -e s+"^BR2_TARGET_BATOCERA_IMAGES[ ]*=[ ]*\"\(.*\)\"[ ]*$"+"\1"+)
if test -z "${BATOCERA_IMAGES_TARGETS}"
then
    echo "no BR2_TARGET_BATOCERA_IMAGES defined." >&2
    exit 1
fi
################################

#### common parent dir to al images #
if echo "${BATOCERA_IMAGES_TARGETS}" | grep -qE '^[^ ]*$'
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
SUFFIXVERSION=$(cat "${TARGET_DIR}/usr/share/batocera/batocera.version" | sed -e s+'^\([0-9\.]*\).*$'+'\1'+) # xx.yy version
SUFFIXDATE=$(date +%Y%m%d)

#### build the images ###########
for BATOCERA_PATHSUBTARGET in ${BATOCERA_IMAGES_TARGETS}
do
    BATOCERA_SUBTARGET=$(basename "${BATOCERA_PATHSUBTARGET}")

    #### prepare the boot dir ######
    BOOTNAMEDDIR="${REGLINUX_BINARIES_DIR}/boot_${BATOCERA_SUBTARGET}"
    rm -rf "${BOOTNAMEDDIR}" || exit 1 # remove in case or rerun
    BATOCERA_POST_IMAGE_SCRIPT="${BR2_EXTERNAL_BATOCERA_PATH}/board/batocera/${BATOCERA_PATHSUBTARGET}/create-boot-script.sh"
    bash "${BATOCERA_POST_IMAGE_SCRIPT}" "${HOST_DIR}" "${BR2_EXTERNAL_BATOCERA_PATH}/board/batocera/${BATOCERA_PATHSUBTARGET}" "${BUILD_DIR}" "${BINARIES_DIR}" "${TARGET_DIR}" "${REGLINUX_BINARIES_DIR}" || exit 1
    # add some common files
    #nope cp -pr "${BINARIES_DIR}/tools"              "${REGLINUX_BINARIES_DIR}/boot/" || exit 1
    cp     "${BINARIES_DIR}/batocera-boot.conf" "${REGLINUX_BINARIES_DIR}/boot/" || exit 1
    echo   "${BATOCERA_SUBTARGET}" > "${REGLINUX_BINARIES_DIR}/boot/boot/batocera.board" || exit 1

    #### boot-$BOARD.tar.zst ###############
    echo "creating images/${BATOCERA_SUBTARGET}/boot-${BATOCERA_SUBTARGET}.tar.zst"
    mkdir -p "${REGLINUX_BINARIES_DIR}/images/${BATOCERA_SUBTARGET}" || exit 1
    (cd "${REGLINUX_BINARIES_DIR}/boot" && tar -I "zstd" -cf "${REGLINUX_BINARIES_DIR}/images/${BATOCERA_SUBTARGET}/boot-${BATOCERA_SUBTARGET}.tar.zst" *) || exit 1

    # create *.img
    if [ "${BATOCERA_LOWER_TARGET}" = "${BATOCERA_SUBTARGET}" ]; then
        BATOCERAIMG="${REGLINUX_BINARIES_DIR}/images/${BATOCERA_SUBTARGET}/reglinux-${BATOCERA_SUBTARGET}-${SUFFIXVERSION}-${SUFFIXDATE}.img"
    else
        BATOCERAIMG="${REGLINUX_BINARIES_DIR}/images/${BATOCERA_SUBTARGET}/reglinux-${BATOCERA_LOWER_TARGET}-${BATOCERA_SUBTARGET}-${SUFFIXVERSION}-${SUFFIXDATE}.img"
    fi
    echo "creating images/${BATOCERA_SUBTARGET}/"$(basename "${BATOCERAIMG}")"..." >&2
    rm -rf "${GENIMAGE_TMP}" || exit 1
    GENIMAGEDIR="${BR2_EXTERNAL_BATOCERA_PATH}/board/batocera/${BATOCERA_PATHSUBTARGET}"
    GENIMAGEFILE="${GENIMAGEDIR}/genimage.cfg"
    FILES=$(find "${REGLINUX_BINARIES_DIR}/boot" -type f | sed -e s+"^${REGLINUX_BINARIES_DIR}/boot/\(.*\)$"+"file \1 \{ image = '\1' }"+ | tr '\n' '@')
    cat "${GENIMAGEFILE}" | sed -e s+'@files'+"${FILES}"+ | tr '@' '\n' > "${REGLINUX_BINARIES_DIR}/genimage.cfg" || exit 1

    # install syslinux
    if grep -qE "^BR2_TARGET_SYSLINUX=y$" "${BR2_CONFIG}"
    then
	GENIMAGEBOOTFILE="${GENIMAGEDIR}/genimage-boot.cfg"
	echo "installing syslinux" >&2
	cat "${GENIMAGEBOOTFILE}" | sed -e s+'@files'+"${FILES}"+ | tr '@' '\n' > "${REGLINUX_BINARIES_DIR}/genimage-boot.cfg" || exit 1
    genimage --rootpath="${TARGET_DIR}" --inputpath="${REGLINUX_BINARIES_DIR}/boot" --outputpath="${REGLINUX_BINARIES_DIR}" --config="${REGLINUX_BINARIES_DIR}/genimage-boot.cfg" --tmppath="${GENIMAGE_TMP}" || exit 1
    "${HOST_DIR}/bin/syslinux" -i "${REGLINUX_BINARIES_DIR}/boot.vfat" -d "/boot/syslinux" || exit 1
    # remove genimage temp path as sometimes genimage v14 fails to start
    rm -rf ${GENIMAGE_TMP}
    mkdir ${GENIMAGE_TMP}
    fi
    ###
    "${HOST_DIR}/bin/genimage" --rootpath="${TARGET_DIR}" --inputpath="${REGLINUX_BINARIES_DIR}/boot" --outputpath="${REGLINUX_BINARIES_DIR}" --config="${REGLINUX_BINARIES_DIR}/genimage.cfg" --tmppath="${GENIMAGE_TMP}" || exit 1

    rm -f "${REGLINUX_BINARIES_DIR}/boot.vfat" || exit 1
    rm -f "${REGLINUX_BINARIES_DIR}/userdata.ext4" || exit 1
    mv "${REGLINUX_BINARIES_DIR}/reglinux.img" "${BATOCERAIMG}" || exit 1
    "${HOST_DIR}/usr/bin/pigz" -1 -p 4 "${BATOCERAIMG}" || exit 1

    # delete the boot
    rm -rf "${REGLINUX_BINARIES_DIR}/boot" || exit 1

    # copy the version file needed for version check
    cp "${TARGET_DIR}/usr/share/batocera/batocera.version" "${REGLINUX_BINARIES_DIR}/images/${BATOCERA_SUBTARGET}" || exit 1
done

#### md5 and sha256 #######################
for BATOCERA_PATHSUBTARGET in ${BATOCERA_IMAGES_TARGETS}
do
    BATOCERA_SUBTARGET=$(basename "${BATOCERA_PATHSUBTARGET}")
    if [ "${BATOCERA_LOWER_TARGET}" = "${BATOCERA_SUBTARGET}" ]; then
        BATOCERA_SUBTARGET="${BATOCERA_LOWER_TARGET}"
    fi
    for FILE in "${REGLINUX_BINARIES_DIR}/images/${BATOCERA_SUBTARGET}/boot-${BATOCERA_SUBTARGET}.tar.zst" "${REGLINUX_BINARIES_DIR}/images/${BATOCERA_SUBTARGET}/reglinux-"*".img.gz"
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
cp "${TARGET_DIR}/usr/share/batocera/batocera.version" "${REGLINUX_BINARIES_DIR}" || exit 1
"${BR2_EXTERNAL_BATOCERA_PATH}"/scripts/linux/systemsReport.sh "${PWD}" "${REGLINUX_BINARIES_DIR}" || exit 1
