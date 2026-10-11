#!/bin/bash

# Joy-Con Bluetooth pairing script for Nintendo Switch
# Reads MAC addresses and link keys from switchroot config
# and creates BlueZ pairing info

JOYCON_INI="/flash/switchroot/joycon_mac.ini"

if [[ ! -f "${JOYCON_INI}" ]]; then
    exit 0
fi

parse_ini() {
    local section="$1"
    local key="$2"
    sed -nr "/^\[${section}\]/ { :l /^${key}[ ]*=/ { s/.*=[ ]*//; p; q;}; n; b l;}" "${JOYCON_INI}" | tr -d "\\r\\n"
}

setup_joycon() {
    local idx="$1"
    local bt_mac_addr="$2"

    local jc_type=$(parse_ini "joycon_${idx}" "type")
    local jc_mac=$(parse_ini "joycon_${idx}" "mac")
    local jc_host=$(parse_ini "joycon_${idx}" "host")
    local jc_ltk=$(parse_ini "joycon_${idx}" "ltk")

    [ -z "${jc_type}" ] && jc_type="0"
    [ "${jc_type}" = "0" ] && return 1

    local dev_name=""
    case "${jc_type}" in
        1) dev_name="Joy-Con (L)" ;;
        2) dev_name="Joy-Con (R)" ;;
        3) dev_name="Pro Controller" ;;
        *) return 1 ;;
    esac

    # Use this joycon's host MAC if we don't have one yet
    if [ -z "${BT_MAC_ADDR}" ]; then
        BT_MAC_ADDR="${jc_host}"
    fi

    [ -z "${bt_mac_addr}" ] && bt_mac_addr="${BT_MAC_ADDR}"
    [ -z "${bt_mac_addr}" ] && return 1

    local bt_dir="/var/lib/bluetooth/${bt_mac_addr}"
    mkdir -p "${bt_dir}/${jc_mac}"
    mkdir -p "${bt_dir}/cache"

    # Check if already paired with same key
    if [ -f "${bt_dir}/${jc_mac}/info" ] && grep -q "${jc_ltk}" "${bt_dir}/${jc_mac}/info" 2>/dev/null; then
        return 0
    fi

    cat > "${bt_dir}/${jc_mac}/info" <<EOF
[General]
Name=${dev_name}
Class=0x000508
SupportedTechnologies=BR/EDR;
Trusted=true
Blocked=false
Services=00001000-0000-1000-8000-00805f9b34fb;00001124-0000-1000-8000-00805f9b34fb;00001200-0000-1000-8000-00805f9b34fb;
[LinkKey]
Key=${jc_ltk}
Type=4
PINLength=0

[ConnectionParameters]
MinInterval=5
MaxInterval=15
Latency=120
Timeout=600
EOF

    cat > "${bt_dir}/cache/${jc_mac}" <<EOF
[General]
Name=${dev_name}
EOF
}

BT_MAC_ADDR=""

# Process up to 3 Joy-Con entries
for idx in 00 01 02; do
    setup_joycon "${idx}" "${BT_MAC_ADDR}"
done
