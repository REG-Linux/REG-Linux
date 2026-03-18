#!/bin/bash
# patch-boot-img.sh — Inject REG-Linux /init into a KNULLI Android boot image.
#
# Keeps the KNULLI kernel, ramdisk structure, cmdline, and all header fields
# intact. Only replaces /init inside the existing ramdisk with the provided
# init script, then uses abootimg to update the boot image in-place.
#
# Usage:
#   patch-boot-img.sh <boot.img> <init-script> [abootimg-path]
#
#   boot.img       - KNULLI prebuilt Android boot image (modified in-place)
#   init-script    - REG-Linux init script to inject as /init
#   abootimg-path  - path to abootimg binary (default: abootimg)

set -e

BOOT_IMG="$(readlink -f "$1")"
INIT_SCRIPT="$(readlink -f "$2")"
ABOOTIMG="${3:-abootimg}"

if [ -z "$1" ] || [ -z "$2" ]; then
    echo "Usage: $0 <boot.img> <init-script> [abootimg-path]"
    exit 1
fi

WORK=$(mktemp -d)
trap 'rm -rf "$WORK"' EXIT

echo "Extracting ramdisk from $BOOT_IMG ..."
"$ABOOTIMG" -x "$BOOT_IMG" "$WORK/bootimg.cfg" "$WORK/zImage" "$WORK/initrd.img"

echo "Unpacking KNULLI ramdisk ..."
mkdir "$WORK/ramdisk_root"
gunzip -c "$WORK/initrd.img" | ( cd "$WORK/ramdisk_root" && cpio -idm --quiet )

echo "Injecting REG-Linux /init ..."
cp "$INIT_SCRIPT" "$WORK/ramdisk_root/init"
chmod 755 "$WORK/ramdisk_root/init"

echo "  KNULLI /rdinit: $(head -1 "$WORK/ramdisk_root/rdinit" 2>/dev/null || echo 'not found')"
echo "  REG    /init:   $(head -1 "$WORK/ramdisk_root/init")"

echo "Repacking ramdisk ..."
( cd "$WORK/ramdisk_root" && find . | cpio -o -H newc --quiet ) > "$WORK/new_ramdisk.cpio"
gzip -9 -n < "$WORK/new_ramdisk.cpio" > "$WORK/new_initrd.img"

echo "  old ramdisk: $(wc -c < "$WORK/initrd.img") bytes"
echo "  new ramdisk: $(wc -c < "$WORK/new_initrd.img") bytes"

echo "Updating boot image with abootimg ..."
"$ABOOTIMG" -u "$BOOT_IMG" -r "$WORK/new_initrd.img"

echo "Done: $BOOT_IMG patched in-place"
