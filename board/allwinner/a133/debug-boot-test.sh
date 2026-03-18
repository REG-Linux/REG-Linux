#!/bin/bash
# Create a debug initramfs that feeds the watchdog and writes a diagnostic log
# to the FAT partition. Run with: sudo bash debug-boot-test.sh
DEV=/dev/sda

echo "=== Building debug initramfs and patching boot.img ==="

# Step 1: Extract current boot.img ramdisk
TMPDIR=$(mktemp -d)
dd if=${DEV}1 of=${TMPDIR}/boot.img bs=1M count=15 2>/dev/null

python3 << PYEOF
import struct, gzip, math, os

tmpdir = "${TMPDIR}"

with open(f"{tmpdir}/boot.img", "rb") as f:
    img = f.read()

if img[:8] != b"ANDROID!":
    print("ERROR: not an Android boot image")
    exit(1)

kernel_size  = struct.unpack_from("<I", img, 8)[0]
ramdisk_size = struct.unpack_from("<I", img, 16)[0]
page_size    = struct.unpack_from("<I", img, 36)[0]

kernel_off  = page_size
ramdisk_off = kernel_off + math.ceil(kernel_size / page_size) * page_size

ramdisk_gz = img[ramdisk_off:ramdisk_off + ramdisk_size]
ramdisk = gzip.decompress(ramdisk_gz)

# Write the ramdisk cpio to a temp file
with open(f"{tmpdir}/ramdisk.cpio", "wb") as f:
    f.write(ramdisk)
print(f"Extracted ramdisk: {len(ramdisk)} bytes")

# Extract cpio to see what's inside
os.makedirs(f"{tmpdir}/initramfs", exist_ok=True)
os.system(f"cd {tmpdir}/initramfs && cpio -id < {tmpdir}/ramdisk.cpio 2>/dev/null")

# List contents
print("\\nInitramfs contents (key files):")
for check in ["/init", "/bin/sh", "/bin/busybox", "/bin/mount", "/bin/mkdir",
              "/bin/sleep", "/bin/echo", "/bin/cat", "/sbin/switch_root",
              "/sbin/watchdog", "/bin/watchdog", "/dev/console", "/linuxrc"]:
    full = f"{tmpdir}/initramfs{check}"
    if os.path.exists(full) or os.path.islink(full):
        if os.path.islink(full):
            target = os.readlink(full)
            print(f"  {check} -> {target}")
        elif os.path.isfile(full):
            sz = os.path.getsize(full)
            print(f"  {check} ({sz} bytes)")
        else:
            print(f"  {check} (exists)")
    else:
        print(f"  {check} MISSING!")

# Check busybox architecture
bb = f"{tmpdir}/initramfs/bin/busybox"
if os.path.exists(bb):
    with open(bb, "rb") as f:
        elf = f.read(20)
    if elf[:4] == b"\\x7fELF":
        arch = {0x28: "ARM32", 0xB7: "AArch64", 0x3E: "x86_64"}.get(elf[18], f"unknown(0x{elf[18]:02x})")
        bits = {1: "32-bit", 2: "64-bit"}.get(elf[4], "unknown")
        print(f"\\nBusybox: {bits} {arch}")
    else:
        print(f"\\nBusybox: not ELF? first bytes: {elf[:8].hex()}")

# Check init script header
init_path = f"{tmpdir}/initramfs/init"
if os.path.exists(init_path):
    with open(init_path, "r") as f:
        lines = f.readlines()[:5]
    print(f"\\nInit script first lines:")
    for l in lines:
        print(f"  {l.rstrip()}")
PYEOF

echo ""
echo "=== Now creating patched init with debug output ==="

# Step 2: Create a debug wrapper init
cat > ${TMPDIR}/initramfs/init.debug << 'INITEOF'
#!/bin/sh
# Debug init — feeds watchdog, writes diagnostic log to FAT

# Feed watchdog IMMEDIATELY using raw device write (no watchdog binary needed)
# Opening /dev/watchdog0 starts the watchdog; writing any byte feeds it
exec 3>/dev/watchdog0 2>/dev/null
(while true; do echo >&3 2>/dev/null; sleep 2; done) &
WDPID=$!

LOG="/debug-log.txt"
echo "=== REG-Linux debug init ===" > $LOG
echo "uptime: $(cat /proc/uptime 2>/dev/null)" >> $LOG

# Step-by-step init with logging
echo "step 1: mount proc" >> $LOG
mount -t proc proc /proc 2>>$LOG && echo "  OK" >> $LOG || echo "  FAIL" >> $LOG

echo "step 2: mount sysfs" >> $LOG
mount -t sysfs sysfs /sys 2>>$LOG && echo "  OK" >> $LOG || echo "  FAIL" >> $LOG

echo "step 3: mount devtmpfs" >> $LOG
mount -t devtmpfs devtmpfs /dev 2>>$LOG && echo "  OK" >> $LOG || echo "  FAIL" >> $LOG

# Re-open watchdog on proper devtmpfs
exec 3>/dev/watchdog0 2>/dev/null

echo "step 4: list block devices" >> $LOG
ls -la /dev/mmcblk* >> $LOG 2>&1
ls -la /dev/sd* >> $LOG 2>&1

echo "step 5: try mounting FAT partitions" >> $LOG
mkdir -p /mnt
for part in /dev/mmcblk0p4 /dev/mmcblk0p1 /dev/mmcblk1p4 /dev/mmcblk1p1; do
    if [ -e "$part" ]; then
        echo "  trying $part..." >> $LOG
        if mount -t vfat "$part" /mnt 2>>$LOG; then
            echo "  mounted $part OK" >> $LOG
            ls /mnt/ >> $LOG 2>&1
            # Write the log there
            cp $LOG /mnt/INIT_DEBUG.txt 2>>$LOG
            # Also test LABEL mount
            umount /mnt
        fi
    fi
done

# Try LABEL mount (what our real init does)
echo "step 6: try LABEL=REGLINUX mount" >> $LOG
mount -o ro "LABEL=REGLINUX" /mnt 2>>$LOG && echo "  LABEL mount OK" >> $LOG || echo "  LABEL mount FAIL" >> $LOG
if mountpoint -q /mnt 2>/dev/null; then
    ls /mnt/ >> $LOG 2>&1
    ls /mnt/boot/ >> $LOG 2>&1
    # Write final log
    mount -o remount,rw /mnt 2>>$LOG
    cp $LOG /mnt/INIT_DEBUG.txt
    echo "step 7: log written to FAT" >> $LOG
    cp $LOG /mnt/INIT_DEBUG.txt
    umount /mnt
fi

echo "step 8: debug init done, sleeping forever (watchdog keeps running)" >> $LOG

# Keep feeding watchdog and stay alive
while true; do
    echo >&3 2>/dev/null
    sleep 2
done
INITEOF
chmod 755 ${TMPDIR}/initramfs/init.debug

# Step 3: Replace init with debug version, keeping original
mv ${TMPDIR}/initramfs/init ${TMPDIR}/initramfs/init.real
mv ${TMPDIR}/initramfs/init.debug ${TMPDIR}/initramfs/init

# Step 4: Repack cpio
echo "Repacking cpio..."
(cd ${TMPDIR}/initramfs && find . | LC_ALL=C sort | cpio --quiet -o -H newc) > ${TMPDIR}/new_ramdisk.cpio

# Step 5: Gzip compress
echo "Compressing..."
gzip -9 < ${TMPDIR}/new_ramdisk.cpio > ${TMPDIR}/new_ramdisk.cpio.gz

# Step 6: Repack into boot.img
python3 << PYEOF
import struct, math

tmpdir = "${TMPDIR}"

with open(f"{tmpdir}/boot.img", "rb") as f:
    img = bytearray(f.read())

kernel_size  = struct.unpack_from("<I", img, 8)[0]
page_size    = struct.unpack_from("<I", img, 36)[0]

kernel_off   = page_size
kernel_end   = kernel_off + math.ceil(kernel_size / page_size) * page_size

with open(f"{tmpdir}/new_ramdisk.cpio.gz", "rb") as f:
    new_ramdisk = f.read()

# Update ramdisk_size in header
struct.pack_into("<I", img, 16, len(new_ramdisk))
# Clear stale SHA1
img[576:608] = b'\x00' * 32

# Also patch cmdline for verbose output
new_cmdline = b'loglevel=7 initcall_debug=0 console=tty0 console=ttyS0,115200 rootwait'
img[64:64+512] = new_cmdline.ljust(512, b'\x00')

# Build output: header pages + kernel pages + new ramdisk pages
def pad(data, ps):
    rem = len(data) % ps
    return data + b'\x00' * (ps - rem) if rem else data

header = bytes(img[:page_size])
kernel = img[kernel_off:kernel_off + kernel_size]

out = header + pad(kernel, page_size) + pad(new_ramdisk, page_size)

with open(f"{tmpdir}/boot.img.patched", "wb") as f:
    f.write(out)
print(f"Patched boot.img: {len(out)} bytes (ramdisk: {len(new_ramdisk)} bytes)")
PYEOF

echo ""
echo "=== Writing patched boot.img to ${DEV}1 ==="
dd if=${TMPDIR}/boot.img.patched of=${DEV}1 bs=1M 2>/dev/null
sync

echo "=== Cleaning up ==="
rm -rf ${TMPDIR}

echo ""
echo "Done! Boot the device, wait 30 seconds, then power off and plug the SD back in."
echo "Check for /media/romain/REGLINUX/INIT_DEBUG.txt — it will tell us exactly where boot fails."
