#!/bin/bash

ARCHS="x86_64 odroidxu4 bcm2835 bcm2836 bcm2837 bcm2711 bcm2712 rk3128 rk3288 rk3326 rk3328 rk3399 rk3568 rk3588 s812 s905 s905gen2 s905gen3 s9gen4 s922x a3gen2 cha h3 h5 h6 h616 jh7110 k1 jz4770"

BR_DIR=$1
REGLINUX_BINARIES_DIR=$2
if ! test -d "${BR_DIR}"
then
    echo "${0} <BR_DIR>" >&2
    exit 1
fi

# create temporary directory
TMP_DIR="/tmp/br_systemreport_${$}"
mkdir -p "${TMP_DIR}" || exit 1
TMP_CONFIGS="${TMP_DIR}/configs"
mkdir -p "${TMP_CONFIGS}" || exit 1

# create configs files
for ARCH in ${ARCHS}
do
    (
    echo "generating .config for ${ARCH}" >&2
    TMP_CONFIG="${TMP_DIR}/configs_tmp/${ARCH}"
    mkdir -p "${TMP_CONFIG}" "${TMP_CONFIGS}" || exit 1

    # generate the defconfig
    "${BR2_EXTERNAL_BATOCERA_PATH}/configs/createDefconfig.sh" "${BR2_EXTERNAL_BATOCERA_PATH}/configs/batocera-${ARCH}"

    (make O="${TMP_CONFIG}" -C ${BR_DIR} BR2_EXTERNAL="${BR2_EXTERNAL_BATOCERA_PATH}" "batocera-${ARCH}_defconfig" > /dev/null) || exit 1
    cp "${TMP_CONFIG}/.config" "${TMP_CONFIGS}/config_${ARCH}" || exit 1
    ) &

    # allow to execute up to 8 jobs in parallel
    if [[ $(jobs -r -p | wc -l) -ge 8 ]]; then
        # now there are 8 jobs already running, so wait here for any job
        # to be finished so there is a place to start next one.
        wait -n
    fi
done

# wait for jobs to finish and do an fs sync
while [[ $(jobs -r -p | wc -l) -ge 1 ]]; do wait -n; done
sync

# reporting
ES_YML="${BR2_EXTERNAL_BATOCERA_PATH}/package/batocera/emulationstation/batocera-es-system/es_systems.yml"
EXP_YML="${BR2_EXTERNAL_BATOCERA_PATH}/package/batocera/emulationstation/batocera-es-system/systems-explanations.yml"
PYGEN="${BR2_EXTERNAL_BATOCERA_PATH}/package/batocera/emulationstation/batocera-es-system/batocera-report-system.py"
HTML_GEN="${BR2_EXTERNAL_BATOCERA_PATH}/package/batocera/emulationstation/batocera-es-system/batocera_systemsReport.html"
DEFAULTSDIR="${BR2_EXTERNAL_BATOCERA_PATH}/package/batocera/core/batocera-configgen/configs"
mkdir -p "${REGLINUX_BINARIES_DIR}" || exit 1
echo python "${PYGEN}" "${ES_YML}" "${EXP_YML}" "${DEFAULTSDIR}" "${TMP_CONFIGS}"
python "${PYGEN}" "${ES_YML}" "${EXP_YML}" "${DEFAULTSDIR}" "${TMP_CONFIGS}" > "${REGLINUX_BINARIES_DIR}/batocera_systemsReport.json" || exit 1
cp "${HTML_GEN}" "${REGLINUX_BINARIES_DIR}" || exit 1

rm -rf "${TMP_DIR}"
exit 0
