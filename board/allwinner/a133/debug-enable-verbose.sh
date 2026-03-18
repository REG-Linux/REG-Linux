#!/bin/bash
# Patch boot.img cmdline on the SD card to enable verbose boot on LCD
# Run with: sudo bash debug-enable-verbose.sh
# This modifies the boot.img on sda1 IN-PLACE (raw partition write)
DEV=/dev/sda

echo "=== Patching boot.img cmdline for verbose LCD output ==="

# boot.img is on partition 1 (14MB)
# Read the header (first 2048 bytes)
TMPIMG=$(mktemp)
dd if=${DEV}1 of=$TMPIMG bs=1M count=15 2>/dev/null

python3 << PYEOF
import struct

with open('$TMPIMG', 'rb') as f:
    data = bytearray(f.read())

magic = data[:8]
if magic != b'ANDROID!':
    print(f'ERROR: not an Android boot image (got {magic})')
    exit(1)

# cmdline is at offset 64, 512 bytes, null-terminated
old_cmdline = data[64:64+512].split(b'\x00')[0].decode('ascii')
print(f'Old cmdline: {old_cmdline}')

# New cmdline: verbose kernel, output on LCD (tty0) and serial
new_cmdline = 'loglevel=7 initcall_debug=0 console=tty0 console=ttyS0,115200 rootwait root=/dev/mmcblk0p4 init=/sbin/init'
print(f'New cmdline: {new_cmdline}')

# Write new cmdline (pad with nulls to 512 bytes)
cmdline_bytes = new_cmdline.encode('ascii') + b'\x00' * (512 - len(new_cmdline))
data[64:64+512] = cmdline_bytes

# Clear SHA1 hash (stale)
data[576:608] = b'\x00' * 32

with open('$TMPIMG', 'wb') as f:
    f.write(data)

print('Cmdline patched OK')
PYEOF

if [ $? -ne 0 ]; then
    echo "ERROR: patching failed"
    rm -f $TMPIMG
    exit 1
fi

echo "Writing patched boot.img back to ${DEV}1..."
dd if=$TMPIMG of=${DEV}1 bs=1M 2>/dev/null
sync
rm -f $TMPIMG

echo "Done. Boot the device and read the kernel messages on the LCD."
echo "Look for where it stops — the last messages will tell us the issue."
