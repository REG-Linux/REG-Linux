#!/bin/sh

# pads requires rw access to the pad
# add udev rules on your computer, or run this script with sudo
# udevadm info -q all -n /dev/bus/usb/001/002
# echo 'SUBSYSTEM=="usb", ENV{ID_MODEL}=="Usb_Gamepad", MODE="0666"' >> /etc/udev/rules.d/99-joysticks-rw.rules

# dd if=/dev/zero of=share.img bs=2G count=1
# mkfs.ext4 share.img

# todo: vsync, screen size

QEMU_DISK_SIZE="${QEMU_DISK_SIZE:-8G}"

if test $# -lt 1; then
    echo "Usage: ${0} <reglinux.img[.gz]> [share image]" >&2
    echo "" >&2
    echo "Accepts .img.gz (auto-decompressed) or .img files." >&2
    echo "The image is automatically grown to ${QEMU_DISK_SIZE} so the rescue" >&2
    echo "system can expand the SHARE partition on first boot." >&2
    echo "Set QEMU_DISK_SIZE=32G to override the target size." >&2
    echo "" >&2
    echo "Network access: ssh root@localhost -p 5555" >&2
    echo "" >&2
    echo "Add pads:" >&2
    echo "  Run evtest to find your pad event name, then:" >&2
    echo '  echo '\''SUBSYSTEM=="usb", ENV{ID_MODEL}=="Bigben_Game_Pad", MODE="0666"'\'' >> /etc/udev/rules.d/99-joystick.rules' >&2
    echo "  sudo udevadm control --reload && replug your pad." >&2
    exit 1
fi

JOYSTICK_CMD=
SEEN_JOYSTICKS=""
for J in /dev/input/event*; do
    DVAL=$(udevadm info -q all -n "${J}" 2>/dev/null) || continue
    if echo "${DVAL}" | grep -qE "^E: ID_INPUT_JOYSTICK=1$"; then
        V_ID=$(echo "${DVAL}" | grep -E "^E: ID_VENDOR_ID=" | sed -e s+"^E: ID_VENDOR_ID="++)
        P_ID=$(echo "${DVAL}" | grep -E "^E: ID_MODEL_ID=" | sed -e s+"^E: ID_MODEL_ID="++)
        DEVKEY="${V_ID}:${P_ID}"
        # Skip if we already added this USB device (multiple event nodes per pad)
        case "${SEEN_JOYSTICKS}" in
            *"${DEVKEY}"*) continue ;;
        esac
        SEEN_JOYSTICKS="${SEEN_JOYSTICKS} ${DEVKEY}"
        JOYSTICK_CMD="${JOYSTICK_CMD} -device usb-host,vendorid=0x${V_ID},productid=0x${P_ID}"
    fi
done

if test -z "${JOYSTICK_CMD}"; then
    echo "***** No joystick found." >&2
fi

REGLINUX_IMG=$1
SHARE_IMG=$2

# Auto-decompress .img.gz files
case "${REGLINUX_IMG}" in
    *.img.gz)
        RAW_IMG="${REGLINUX_IMG%.gz}"
        if [ ! -f "${RAW_IMG}" ]; then
            echo "Decompressing ${REGLINUX_IMG}..." >&2
            gunzip -k "${REGLINUX_IMG}" || { echo "gunzip failed" >&2; exit 1; }
        else
            echo "Using existing ${RAW_IMG} (delete it to re-extract)" >&2
        fi
        REGLINUX_IMG="${RAW_IMG}"
        ;;
esac

if [ ! -f "${REGLINUX_IMG}" ]; then
    echo "Image not found: ${REGLINUX_IMG}" >&2
    exit 1
fi

# Grow the image so the rescue system can expand the SHARE partition.
# truncate --size only extends if the file is smaller (no-op if already big enough).
CURRENT_SIZE=$(stat -c%s "${REGLINUX_IMG}")
TARGET_SIZE=$(numfmt --from=iec "${QEMU_DISK_SIZE}" 2>/dev/null || echo 8589934592)
if [ "${CURRENT_SIZE}" -lt "${TARGET_SIZE}" ]; then
    echo "Growing image to ${QEMU_DISK_SIZE} (from $(numfmt --to=iec "${CURRENT_SIZE}"))..." >&2
    truncate --size="${QEMU_DISK_SIZE}" "${REGLINUX_IMG}" || { echo "truncate failed" >&2; exit 1; }
fi

if test -n "${SHARE_IMG}"; then
    SHARE_CMD="-drive format=raw,file=${SHARE_IMG},if=virtio"
else
    SHARE_CMD=
    echo "***** no share disk set." >&2
fi

qemu-system-x86_64 \
    -cpu host -enable-kvm \
    -smp 4 -m 2048 \
    -vga none -device virtio-gpu-gl-pci -display gtk,gl=on \
    -device virtio-sound-pci \
    -device virtio-net-pci,netdev=net0 \
    -netdev user,id=net0,hostfwd=tcp::5555-:22 \
    -device nec-usb-xhci -device usb-tablet \
    ${JOYSTICK_CMD} \
    -drive "format=raw,file=${REGLINUX_IMG},if=virtio" \
    ${SHARE_CMD}

ret=$?
if [ $ret -ne 0 ]; then
    echo "QEMU exited with error code $ret" >&2
    exit $ret
fi
