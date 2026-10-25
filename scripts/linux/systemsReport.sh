#!/bin/bash

# Derived from the board configs rather than hardcoded: the old fixed list had
# drifted badly (still named h5/h6, merged into sun50i, while missing 20 live
# boards including odroidc5/sm8250/x86_64_v3).
ARCHS=$(ls "${BR2_EXTERNAL_REGLINUX_PATH}"/configs/reglinux-*.board 2>/dev/null |
            sed 's#.*/reglinux-##; s#\.board$##')

BR_DIR=$1
REGLINUX_BINARIES_DIR=$2
if ! test -d "${BR_DIR}" || test -z "${REGLINUX_BINARIES_DIR}"; then
    echo "${0} <BR_DIR> <REGLINUX_BINARIES_DIR>" >&2
    exit 1
fi
if test -z "${ARCHS}"; then
    echo "${0}: no board configs found under ${BR2_EXTERNAL_REGLINUX_PATH}/configs" >&2
    exit 1
fi

# create temporary directory
TMP_DIR="/tmp/br_systemreport_${$}"
mkdir -p "${TMP_DIR}" || exit 1
TMP_CONFIGS="${TMP_DIR}/configs"
mkdir -p "${TMP_CONFIGS}" || exit 1

# create configs files
for ARCH in ${ARCHS}; do
    (
        echo "generating .config for ${ARCH}" >&2
        TMP_CONFIG="${TMP_DIR}/configs_tmp/${ARCH}"
        mkdir -p "${TMP_CONFIG}" "${TMP_CONFIGS}" || exit 1

        # generate the defconfig
        "${BR2_EXTERNAL_REGLINUX_PATH}/configs/createDefconfig.sh" "${BR2_EXTERNAL_REGLINUX_PATH}/configs/reglinux-${ARCH}"

        (make O="${TMP_CONFIG}" -C ${BR_DIR} BR2_EXTERNAL="${BR2_EXTERNAL_REGLINUX_PATH}" "reglinux-${ARCH}_defconfig" >/dev/null) || exit 1
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
ES_YML="${BR2_EXTERNAL_REGLINUX_PATH}/package/frontend/es-system/es_systems.yml"
EXP_YML="${BR2_EXTERNAL_REGLINUX_PATH}/package/frontend/es-system/systems-explanations.yml"
PYGEN="${BR2_EXTERNAL_REGLINUX_PATH}/package/frontend/es-system/report-system.py"
HTML_GEN="${BR2_EXTERNAL_REGLINUX_PATH}/package/frontend/es-system/systemsReport.html"
DEFAULTSDIR="${BR2_EXTERNAL_REGLINUX_PATH}/package/system/reglinux-launcher-defaults/configs"
mkdir -p "${REGLINUX_BINARIES_DIR}" || exit 1
echo python "${PYGEN}" "${ES_YML}" "${EXP_YML}" "${DEFAULTSDIR}" "${TMP_CONFIGS}"
python "${PYGEN}" "${ES_YML}" "${EXP_YML}" "${DEFAULTSDIR}" "${TMP_CONFIGS}" >"${REGLINUX_BINARIES_DIR}/reglinux_systemsReport.json" || exit 1
cp "${HTML_GEN}" "${REGLINUX_BINARIES_DIR}" || exit 1

rm -rf "${TMP_DIR}"
exit 0
