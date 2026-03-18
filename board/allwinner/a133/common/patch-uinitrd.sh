#!/bin/bash
# patch-uinitrd.sh — Inject REG-Linux /init into a gzip-compressed cpio initrd.
#
# For devices like xu20-v32 where the initramfs is a standalone gzip cpio
# file (uInitrd) on the FAT partition, rather than inside an Android boot image.
#
# Usage:
#   patch-uinitrd.sh <uinitrd> <init-script>
#
#   uinitrd      - gzip-compressed cpio initrd (modified in-place)
#   init-script  - REG-Linux init script to inject as /init

set -e

UINITRD="$(readlink -f "$1")"
INIT_SCRIPT="$(readlink -f "$2")"

if [ -z "$1" ] || [ -z "$2" ]; then
    echo "Usage: $0 <uinitrd> <init-script>"
    exit 1
fi

WORK=$(mktemp -d)
trap 'rm -rf "$WORK"' EXIT

echo "Decompressing $UINITRD ..."
gunzip -c "$UINITRD" > "$WORK/initrd.cpio"

echo "Unpacking initrd ..."
mkdir "$WORK/ramdisk_root"
( cd "$WORK/ramdisk_root" && cpio -idm --quiet < "$WORK/initrd.cpio" )

echo "Injecting REG-Linux /init ..."
cp "$INIT_SCRIPT" "$WORK/ramdisk_root/init"
chmod 755 "$WORK/ramdisk_root/init"

echo "  original /init: $(head -1 "$WORK/initrd.cpio" 2>/dev/null | head -c 40)"
echo "  REG      /init: $(head -1 "$WORK/ramdisk_root/init")"

echo "Repacking initrd ..."
( cd "$WORK/ramdisk_root" && find . | cpio -o -H newc --quiet ) > "$WORK/new_initrd.cpio"
gzip -9 -n < "$WORK/new_initrd.cpio" > "$WORK/new_uinitrd.gz"

echo "  old initrd: $(wc -c < "$UINITRD") bytes"
echo "  new initrd: $(wc -c < "$WORK/new_uinitrd.gz") bytes"

cp "$WORK/new_uinitrd.gz" "$UINITRD"

echo "Done: $UINITRD patched in-place"
