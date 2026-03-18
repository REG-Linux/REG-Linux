#!/bin/bash
# Diagnose REG-Linux A133 SD card — run with: sudo bash diagnose-sdcard.sh [/dev/sdX]
set -e

# Colors
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; NC='\033[0m'
ok()   { echo -e "${GREEN}[OK]${NC} $1"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
fail() { echo -e "${RED}[FAIL]${NC} $1"; }

DEV="${1:-/dev/sda}"
MOUNT_POINT=""
OWN_MOUNT=0
TMPDIR=$(mktemp -d)
trap 'cd /; [ "$OWN_MOUNT" = 1 ] && umount "$MOUNT_POINT" 2>/dev/null; rm -rf "$TMPDIR"' EXIT

echo "=========================================="
echo " REG-Linux A133 SD Card Diagnostic"
echo "=========================================="
echo "Device: ${DEV}"
echo ""

# --- 1. Partition layout ---
echo "=== 1. PARTITION LAYOUT ==="
if [ ! -b "${DEV}" ]; then
    fail "Device ${DEV} not found"
    exit 1
fi
fdisk -l "${DEV}" 2>&1 | grep -E "^${DEV}|^Disk ${DEV}"
echo ""
echo "  All partitions:"
for p in ${DEV}1 ${DEV}2 ${DEV}3 ${DEV}4 ${DEV}5 ${DEV}6 ${DEV}7 ${DEV}8; do
    [ -b "$p" ] || continue
    LABEL=$(blkid -s LABEL -o value "$p" 2>/dev/null || true)
    FSTYPE=$(blkid -s TYPE -o value "$p" 2>/dev/null || true)
    SIZE=$(blockdev --getsize64 "$p" 2>/dev/null || echo "?")
    echo "  $p: label=$LABEL type=$FSTYPE size=$((SIZE/1024/1024))MB"
done
echo ""

# --- 2. Find and mount REGLINUX partition ---
echo "=== 2. REGLINUX FAT PARTITION ==="
REGPART=""
for p in ${DEV}1 ${DEV}2 ${DEV}3 ${DEV}4 ${DEV}5 ${DEV}6 ${DEV}7 ${DEV}8; do
    [ -b "$p" ] || continue
    LABEL=$(blkid -s LABEL -o value "$p" 2>/dev/null || true)
    if [ "$LABEL" = "REGLINUX" ]; then
        REGPART="$p"
        break
    fi
done

if [ -z "$REGPART" ]; then
    fail "No partition with LABEL=REGLINUX found!"
    exit 1
fi

# Check if already mounted
MOUNT_POINT=$(findmnt -rn -S "$REGPART" -o TARGET 2>/dev/null | head -1)
if [ -z "$MOUNT_POINT" ]; then
    MOUNT_POINT="${TMPDIR}/mnt"
    mkdir -p "$MOUNT_POINT"
    mount -o ro "$REGPART" "$MOUNT_POINT" || { fail "Cannot mount $REGPART"; exit 1; }
    OWN_MOUNT=1
    ok "Mounted $REGPART at $MOUNT_POINT"
else
    ok "$REGPART already mounted at $MOUNT_POINT"
fi
echo ""

# --- 3. FAT contents ---
echo "=== 3. FAT ROOT CONTENTS ==="
ls -la "$MOUNT_POINT"/
echo ""

echo "=== 4. BOOT DIRECTORY ==="
if [ ! -d "$MOUNT_POINT/boot" ]; then
    fail "No boot/ directory!"
else
    ls -la "$MOUNT_POINT/boot/"
fi
echo ""

# --- 5. Check required boot files ---
echo "=== 5. REQUIRED FILES CHECK ==="
for f in boot/reglinux boot/rescue boot/modules boot/firmware boot/linux boot/initrd.lz4; do
    if [ -f "$MOUNT_POINT/$f" ]; then
        SIZE=$(stat -c%s "$MOUNT_POINT/$f")
        ok "$f ($SIZE bytes)"
    else
        fail "$f MISSING"
    fi
done
for f in bootlogo.bmp system-boot.conf extlinux/extlinux.conf; do
    if [ -e "$MOUNT_POINT/$f" ]; then
        ok "$f (present)"
    else
        warn "$f missing"
    fi
done
echo ""

# --- 6. Squashfs compression check ---
echo "=== 6. SQUASHFS IMAGES ==="
for f in boot/reglinux boot/modules boot/firmware boot/rescue; do
    [ -f "$MOUNT_POINT/$f" ] || continue
    echo "  --- $f ---"
    if command -v unsquashfs >/dev/null 2>&1; then
        unsquashfs -s "$MOUNT_POINT/$f" 2>&1 | grep -E "Compression|Block size|High Comp" | sed 's/^/    /'
    else
        file "$MOUNT_POINT/$f" 2>&1 | sed 's/^/    /'
    fi
done
echo ""

# --- 7. Try mounting squashfs images on host ---
echo "=== 7. SQUASHFS MOUNT TEST (host kernel) ==="
SQMNT="${TMPDIR}/sqtest"
mkdir -p "$SQMNT"
for f in boot/reglinux boot/modules boot/firmware; do
    [ -f "$MOUNT_POINT/$f" ] || continue
    if mount -o ro -t squashfs "$MOUNT_POINT/$f" "$SQMNT" 2>"${TMPDIR}/sqerr"; then
        COUNT=$(find "$SQMNT" -maxdepth 2 2>/dev/null | wc -l)
        ok "$f mounts OK ($COUNT entries at depth<=2)"
        # For modules, show what's inside
        if echo "$f" | grep -q modules; then
            echo "    Contents: $(ls "$SQMNT"/ 2>/dev/null)"
        fi
        umount "$SQMNT"
    else
        ERR=$(cat "${TMPDIR}/sqerr")
        fail "$f MOUNT FAILED: $ERR"
    fi
done
echo ""

# --- 8. Initrd analysis ---
echo "=== 8. INITRD ANALYSIS ==="
INITRD="$MOUNT_POINT/boot/initrd.lz4"
if [ -f "$INITRD" ]; then
    file "$INITRD"
    CPIOFILE="${TMPDIR}/initrd.cpio"
    python3 -c "
import sys
try:
    import lz4.block
    with open('$INITRD','rb') as f:
        data = f.read()
    dec = lz4.block.decompress(data[8:], uncompressed_size=len(data)*10)
    with open('$CPIOFILE','wb') as o:
        o.write(dec)
    print(f'  Decompressed: {len(dec)} bytes (lz4 block)')
except Exception as e:
    try:
        import lz4.frame
        with open('$INITRD','rb') as f:
            data = f.read()
        dec = lz4.frame.decompress(data)
        with open('$CPIOFILE','wb') as o:
            o.write(dec)
        print(f'  Decompressed: {len(dec)} bytes (lz4 frame)')
    except Exception as e2:
        print(f'  FAIL: cannot decompress: {e} / {e2}')
        sys.exit(1)
" 2>&1

    if [ -f "$CPIOFILE" ]; then
        INITDIR="${TMPDIR}/initramfs"
        mkdir -p "$INITDIR"
        (cd "$INITDIR" && cpio -id < "$CPIOFILE" 2>/dev/null)

        echo ""
        echo "  Key files:"
        for check in init bin/busybox bin/sh bin/mount sbin/switch_root sbin/watchdog linuxrc; do
            FULL="$INITDIR/$check"
            if [ -e "$FULL" ] || [ -L "$FULL" ]; then
                if [ -L "$FULL" ]; then
                    ok "  /$check -> $(readlink "$FULL")"
                else
                    ok "  /$check ($(stat -c%s "$FULL") bytes)"
                fi
            else
                fail "  /$check MISSING"
            fi
        done

        echo ""
        echo "  Busybox:"
        file "$INITDIR/bin/busybox" 2>&1 | sed 's/^/    /'

        echo ""
        echo "  Init script analysis:"
        if [ -f "$INITDIR/init" ]; then
            LINES=$(wc -l < "$INITDIR/init")
            echo "    Total lines: $LINES"

            grep -q "DEBUGLOG"                     "$INITDIR/init" && ok "  Has debug logging"          || fail "  NO debug logging (custom init not merged!)"
            grep -q "watchdog"                     "$INITDIR/init" && ok "  Has watchdog feeding"        || fail "  NO watchdog feeding"
            grep -q "devtmpfs"                     "$INITDIR/init" && ok "  Has devtmpfs mount"          || fail "  NO devtmpfs mount"
            grep -q "continuing after modules"     "$INITDIR/init" && ok "  Modules mount is non-fatal"  || warn "  Modules mount is FATAL"
            grep -q "LABEL=REGLINUX"               "$INITDIR/init" && ok "  Uses LABEL=REGLINUX"         || fail "  Does NOT use LABEL=REGLINUX"

            echo ""
            echo "  Modules mount code in init:"
            grep -n "do_mount_modules\|mount.*modules" "$INITDIR/init" | sed 's/^/    /'

            echo ""
            echo "  Full init script:"
            echo "  ----"
            cat -n "$INITDIR/init" | sed 's/^/    /'
            echo "  ----"
        fi
    fi
fi
echo ""

# --- 9. Boot.img analysis (partition 1) ---
echo "=== 9. BOOT.IMG (${DEV}1) ==="
BOOTPART="${DEV}1"
if [ -b "$BOOTPART" ]; then
    python3 -c "
import struct, math
with open('$BOOTPART', 'rb') as f:
    img = f.read(4096)
if img[:8] != b'ANDROID!':
    print('  NOT an Android boot image (magic: ' + img[:8].hex() + ')')
else:
    kernel_size  = struct.unpack_from('<I', img, 8)[0]
    ramdisk_size = struct.unpack_from('<I', img, 16)[0]
    page_size    = struct.unpack_from('<I', img, 36)[0]
    cmdline      = img[64:64+512].split(b'\x00')[0].decode('ascii','replace')
    print(f'  Magic: ANDROID!')
    print(f'  Page size: {page_size}')
    print(f'  Kernel size: {kernel_size} ({kernel_size/1024/1024:.1f} MB)')
    print(f'  Ramdisk size: {ramdisk_size} ({ramdisk_size/1024/1024:.1f} MB)')
    print(f'  Cmdline: {cmdline}')
    print()
    # Check ramdisk content
    kernel_pages = math.ceil(kernel_size / page_size)
    ramdisk_off = (1 + kernel_pages) * page_size
    with open('$BOOTPART', 'rb') as f:
        f.seek(ramdisk_off)
        rd = f.read(min(ramdisk_size, 4096))
    print(f'  Ramdisk first bytes: {rd[:16].hex()}')
    if rd[:2] == b'\x1f\x8b':
        print('  Ramdisk format: gzip')
    elif rd[:4] == b'\x04\x22\x4d\x18':
        print('  Ramdisk format: lz4 frame')
    elif rd[:4] == b'\x02\x21\x4c\x18':
        print('  Ramdisk format: lz4 legacy')
    else:
        print(f'  Ramdisk format: unknown (magic {rd[:4].hex()})')
    # Check if it contains our init
    import gzip, io
    with open('$BOOTPART', 'rb') as f:
        f.seek(ramdisk_off)
        rd_full = f.read(ramdisk_size)
    try:
        cpio = gzip.decompress(rd_full)
        has_reglinux = b'REGLINUX' in cpio
        has_batocera = b'batocera' in cpio or b'BATOCERA' in cpio
        has_do_root  = b'do_root' in cpio
        has_watchdog = b'watchdog' in cpio
        has_debuglog = b'DEBUGLOG' in cpio
        print(f'  Contains REGLINUX: {has_reglinux}')
        print(f'  Contains batocera: {has_batocera}')
        print(f'  Contains do_root:  {has_do_root}')
        print(f'  Contains watchdog: {has_watchdog}')
        print(f'  Contains DEBUGLOG: {has_debuglog}')
    except Exception as e:
        print(f'  Cannot decompress ramdisk: {e}')
" 2>&1
fi
echo ""

# --- 10. Env.img analysis (partition 2) ---
echo "=== 10. U-BOOT ENV (${DEV}2) ==="
ENVPART="${DEV}2"
if [ -b "$ENVPART" ]; then
    python3 -c "
import struct, binascii
with open('$ENVPART', 'rb') as f:
    data = f.read(131072)
crc_stored = struct.unpack_from('<I', data, 0)[0]
flags = data[4]
env_data = data[5:]
crc_calc = binascii.crc32(env_data) & 0xFFFFFFFF

pairs = []
pos = 0
while pos < len(env_data):
    end = env_data.find(b'\x00', pos)
    if end == pos: break
    pairs.append(env_data[pos:end].decode('ascii','replace'))
    pos = end + 1

print(f'  CRC32 stored:  0x{crc_stored:08x}')
print(f'  CRC32 calc:    0x{crc_calc:08x}')
if crc_stored == crc_calc:
    print('  CRC: OK')
else:
    print('  CRC: MISMATCH!')
print(f'  Flags: 0x{flags:02x}')
print(f'  Variables: {len(pairs)}')
for p in pairs:
    if len(p) > 150:
        k = p.split('=',1)[0]
        v = p.split('=',1)[1] if '=' in p else ''
        print(f'    {k}={v[:120]}...')
    else:
        print(f'    {p}')

env_dict = dict(p.split('=',1) for p in pairs if '=' in p)
print()
if 'rdinit' in env_dict:
    v = env_dict['rdinit']
    if v == '/init':
        print(f'  \033[0;32m[OK]\033[0m rdinit={v}')
    else:
        print(f'  \033[0;31m[FAIL]\033[0m rdinit={v} (expected /init)')
else:
    print('  [INFO] No rdinit variable')
if 'init' in env_dict:
    print(f'  init={env_dict[\"init\"]}')
" 2>&1
fi
echo ""

# --- 11. Partitions blobs ---
echo "=== 11. PARTITIONS DIRECTORY ==="
PARTDIR="$MOUNT_POINT/partitions"
if [ -d "$PARTDIR" ]; then
    ls -la "$PARTDIR"/
    for f in "$PARTDIR"/*; do
        [ -e "$f" ] || continue
        if [ -L "$f" ] && [ ! -e "$f" ]; then
            fail "BROKEN symlink: $f -> $(readlink "$f")"
        fi
    done
else
    warn "No partitions/ directory"
fi
echo ""

# --- 12. Debug logs ---
echo "=== 12. DEBUG LOGS ==="
for f in BOOT_DEBUG.txt INIT_DEBUG.txt; do
    if [ -f "$MOUNT_POINT/$f" ]; then
        ok "$f found:"
        cat "$MOUNT_POINT/$f"
        echo ""
    fi
done
[ ! -f "$MOUNT_POINT/BOOT_DEBUG.txt" ] && [ ! -f "$MOUNT_POINT/INIT_DEBUG.txt" ] && warn "No debug logs found"
echo ""

# --- 13. Kernel config from source ---
echo "=== 13. KERNEL SQUASHFS CONFIG (source) ==="
KCFG="$(dirname "$(readlink -f "$0")")/linux-sunxi64-legacy.config"
if [ -f "$KCFG" ]; then
    grep -E "SQUASHFS|OVERLAY_FS|BLK_DEV_LOOP" "$KCFG" | sed 's/^/  /'
else
    warn "Kernel config not found at $KCFG"
fi
echo ""

# --- 14. Compare FAT initrd vs boot.img ramdisk ---
echo "=== 14. INITRD CONSISTENCY ==="
if [ -f "$MOUNT_POINT/boot/initrd.lz4" ]; then
    FAT_SIZE=$(stat -c%s "$MOUNT_POINT/boot/initrd.lz4")
    echo "  FAT initrd.lz4: $FAT_SIZE bytes"
fi
if [ -b "${DEV}1" ]; then
    python3 -c "
import struct, math
with open('${DEV}1', 'rb') as f:
    img = f.read(4096)
if img[:8] == b'ANDROID!':
    ramdisk_size = struct.unpack_from('<I', img, 16)[0]
    print(f'  boot.img ramdisk: {ramdisk_size} bytes')
" 2>&1
fi
echo ""

echo "=========================================="
echo " DIAGNOSTIC COMPLETE"
echo "=========================================="
