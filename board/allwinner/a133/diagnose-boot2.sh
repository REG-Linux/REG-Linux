#!/bin/bash
# Diagnose A133 boot issues — round 2
# Run with: sudo bash diagnose-boot2.sh
DEV=/dev/sda

echo "=== 1. Verify env.img rdinit fix ==="
# env partition is sda2 (1MB)
echo "Reading env partition (sda2)..."
ENV_DATA=$(dd if=${DEV}2 bs=1 skip=5 count=2000 2>/dev/null)
echo "$ENV_DATA" | strings | grep -E '^rdinit='
echo "$ENV_DATA" | strings | grep -E '^init='
echo "$ENV_DATA" | strings | grep -E '^bootcmd='

echo ""
echo "=== 2. Verify boot.img ramdisk is REG-Linux ==="
TMPBOOT=$(mktemp)
dd if=$DEV bs=1M skip=36 count=16 of=$TMPBOOT 2>/dev/null
python3 -c "
import struct, gzip
with open('$TMPBOOT', 'rb') as f:
    hdr = f.read(2048)
    kernel_size = struct.unpack_from('<I', hdr, 8)[0]
    ramdisk_size = struct.unpack_from('<I', hdr, 16)[0]
    page_size = struct.unpack_from('<I', hdr, 36)[0]
    cmdline = hdr[64:64+512].split(b'\x00')[0].decode('ascii','replace')
    print(f'boot.img cmdline: {cmdline}')
    print(f'Kernel: {kernel_size} bytes, Ramdisk: {ramdisk_size} bytes')
    kernel_pages = (kernel_size + page_size - 1) // page_size
    ramdisk_offset = (1 + kernel_pages) * page_size
    f.seek(ramdisk_offset)
    ramdisk_data = f.read(ramdisk_size)
    try:
        cpio = gzip.decompress(ramdisk_data)
        if b'/init' in cpio:
            print('Ramdisk has /init: YES')
        if b'rdinit' in cpio:
            print('Ramdisk has rdinit ref: YES')
        if b'REGLINUX' in cpio:
            print('Ramdisk identity: REG-Linux OK')
        elif b'BATOCERA' in cpio or b'batocera' in cpio:
            print('Ramdisk identity: STILL KNULLI!')
        if b'do_root' in cpio:
            print('Ramdisk has do_root: YES')
        if b'watchdog' in cpio:
            print('Ramdisk has watchdog: YES')
        # Check for /rdinit symlink or file in the cpio
        if b'rdinit' in cpio:
            # Look for the cpio entry
            pos = cpio.find(b'rdinit')
            context = cpio[max(0,pos-20):pos+20]
            print(f'rdinit context in cpio: {context}')
    except Exception as e:
        print(f'Cannot decompress: {e}')
"
rm -f $TMPBOOT

echo ""
echo "=== 3. FAT partition contents ==="
mount | grep REGLINUX
ls -la /media/romain/REGLINUX/ 2>/dev/null || ls -la /media/*/REGLINUX/ 2>/dev/null
ls -la /media/romain/REGLINUX/boot/ 2>/dev/null || ls -la /media/*/REGLINUX/boot/ 2>/dev/null

echo ""
echo "=== 4. Check partitions/ on FAT ==="
ls -la /media/romain/REGLINUX/partitions/ 2>/dev/null || ls -la /media/*/REGLINUX/partitions/ 2>/dev/null

echo ""
echo "=== 5. Verify env.img on FAT partition (used by genimage for env partition) ==="
if [ -f /media/romain/REGLINUX/partitions/env.img ]; then
    dd if=/media/romain/REGLINUX/partitions/env.img bs=1 skip=5 count=2000 2>/dev/null | strings | grep -E '^rdinit='
    echo "(above is the FAT copy — the raw partition sda2 is what U-Boot actually reads)"
fi

echo ""
echo "=== 6. Raw env partition hex (first 256 bytes after CRC+flags) ==="
dd if=${DEV}2 bs=1 skip=5 count=256 2>/dev/null | strings

echo ""
echo "=== 7. Kernel dmesg from last boot (if accessible) ==="
# If the system partially booted, there might be pstore or dmesg
if [ -d /sys/fs/pstore ]; then
    echo "pstore entries:"
    ls -la /sys/fs/pstore/
    cat /sys/fs/pstore/console-ramoops-0 2>/dev/null | tail -50
fi
