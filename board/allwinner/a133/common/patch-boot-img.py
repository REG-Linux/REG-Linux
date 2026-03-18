#!/usr/bin/env python3
"""
patch-boot-img.py - Replace the ramdisk in a KNULLI Android boot image with
                    REG-Linux's own initrd, keeping the KNULLI kernel intact.

The KNULLI prebuilt boot.img bundles a kernel + KNULLI ramdisk (gzip-cpio).
REG-Linux builds its own initrd (rootfs.cpio) with the correct /init that
understands the REG-Linux filesystem layout (reglinux squashfs, LABEL=REGLINUX
boot partition, modules/firmware/rescue update handling).

This script swaps the ramdisk, recompressing with gzip so the unmodified
KNULLI kernel can always decompress it (CONFIG_RD_GZIP is universally enabled).
The kernel and all header fields (load addresses, cmdline, etc.) are preserved.

Usage:
    patch-boot-img.py <boot.img> <rootfs.cpio> [output.img]

    boot.img     - input Android boot image (KNULLI prebuilt)
    rootfs.cpio  - REG-Linux initrd as a plain (uncompressed) cpio archive
    output.img   - output path; defaults to patching boot.img in-place

The script is idempotent: running it twice produces the same result.
"""

import gzip
import hashlib
import io
import math
import struct
import sys

ANDROID_MAGIC = b"ANDROID!"


def parse_header(data):
    if data[:8] != ANDROID_MAGIC:
        sys.exit("ERROR: not an Android boot image (bad magic)")
    return {
        "kernel_size":   struct.unpack_from("<I", data,  8)[0],
        "kernel_addr":   struct.unpack_from("<I", data, 12)[0],
        "ramdisk_size":  struct.unpack_from("<I", data, 16)[0],
        "ramdisk_addr":  struct.unpack_from("<I", data, 20)[0],
        "second_size":   struct.unpack_from("<I", data, 24)[0],
        "second_addr":   struct.unpack_from("<I", data, 28)[0],
        "tags_addr":     struct.unpack_from("<I", data, 32)[0],
        "page_size":     struct.unpack_from("<I", data, 36)[0],
        "dt_size":       struct.unpack_from("<I", data, 40)[0],
        "cmdline":       data[64:64+512].rstrip(b"\x00").decode("ascii", errors="replace"),
    }


def align_up(n, page_size):
    return math.ceil(n / page_size) * page_size


def unpack(img):
    hdr = parse_header(img)
    ps = hdr["page_size"]
    kernel_off  = ps
    ramdisk_off = kernel_off  + align_up(hdr["kernel_size"],  ps)
    second_off  = ramdisk_off + align_up(hdr["ramdisk_size"], ps)
    dt_off      = second_off  + align_up(hdr["second_size"],  ps)
    return (
        hdr,
        img[kernel_off  : kernel_off  + hdr["kernel_size"]],
        img[ramdisk_off : ramdisk_off + hdr["ramdisk_size"]],
        img[second_off  : second_off  + hdr["second_size"]] if hdr["second_size"] else b"",
        img[dt_off      : dt_off      + hdr["dt_size"]]     if hdr["dt_size"]     else b"",
    )


def gzip_compress(data):
    """Compress data with gzip, matching the format the KNULLI kernel expects.

    The Allwinner 4.9.191 kernel's gzip decompressor is picky about the header.
    We use subprocess to call the system gzip which produces a standard header
    with OS=Unix (0x03), matching KNULLI's original ramdisk format.
    """
    import subprocess
    result = subprocess.run(
        ["gzip", "-9", "-n"],
        input=data, capture_output=True, check=True,
    )
    return result.stdout


def pad_to_page(data, page_size):
    rem = len(data) % page_size
    return data + b"\x00" * (page_size - rem) if rem else data


def patch_cmdline(original_cmdline):
    """Patch the kernel cmdline for REG-Linux boot.

    - Remove init= and root= so the kernel boots into the initramfs
    - Ensure rdinit=/init is present (kernel executes our initramfs /init)
    - Set loglevel=7 so kernel messages show on the built-in display
    - Add panic=0 to prevent auto-reboot on kernel panic (aids debugging)
    """
    import re
    cmd = original_cmdline

    # Remove init= — it overrides rdinit= and bypasses the initramfs
    cmd = re.sub(r"\binit=\S+", "", cmd)

    # Remove root= — it tells the kernel to mount a root device directly,
    # skipping the initramfs where our /init lives
    cmd = re.sub(r"\broot=\S+", "", cmd)

    # Remove rootwait — no longer needed without root=
    cmd = re.sub(r"\brootwait\b", "", cmd)

    # Replace or add rdinit
    if "rdinit=" in cmd:
        cmd = re.sub(r"rdinit=\S+", "rdinit=/init", cmd)
    else:
        cmd += " rdinit=/init"

    # Increase loglevel for screen output
    cmd = re.sub(r"loglevel=\d+", "loglevel=7", cmd)

    # Add panic=0 (don't auto-reboot on kernel panic)
    if "panic=" not in cmd:
        cmd += " panic=0"
    else:
        cmd = re.sub(r"panic=\d+", "panic=0", cmd)

    # Collapse multiple spaces
    cmd = re.sub(r"  +", " ", cmd)

    return cmd.strip()


def compute_id(kernel, ramdisk, second, dt):
    """Compute the Android boot image id (SHA1 hash).

    The hash covers each section's data followed by its size as a LE uint32.
    This matches the standard Android mkbootimg id computation.
    """
    sha = hashlib.sha1()
    sha.update(kernel)
    sha.update(struct.pack("<I", len(kernel)))
    sha.update(ramdisk)
    sha.update(struct.pack("<I", len(ramdisk)))
    sha.update(second)
    sha.update(struct.pack("<I", len(second)))
    if dt:
        sha.update(dt)
        sha.update(struct.pack("<I", len(dt)))
    # 20-byte SHA1 digest + 12 bytes zero padding = 32 bytes
    return sha.digest().ljust(32, b"\x00")


def repack(hdr, header_raw, kernel, new_ramdisk, second, dt, new_cmdline=None):
    ps = hdr["page_size"]
    new_hdr = bytearray(header_raw[:ps])
    struct.pack_into("<I", new_hdr, 16, len(new_ramdisk))  # update ramdisk_size

    # Patch cmdline in header (offset 64, 512 bytes zero-padded)
    if new_cmdline is not None:
        cmd_bytes = new_cmdline.encode("ascii")[:511] + b"\x00"
        new_hdr[64:64+512] = cmd_bytes.ljust(512, b"\x00")

    # Recompute the Android boot image SHA1 id (offset 576, 32 bytes)
    new_hdr[576:608] = compute_id(kernel, new_ramdisk, second, dt)

    out  = bytes(new_hdr)
    out += pad_to_page(kernel,      ps)
    out += pad_to_page(new_ramdisk, ps)
    if second:
        out += pad_to_page(second, ps)
    if dt:
        out += pad_to_page(dt, ps)
    return out


def main():
    if len(sys.argv) < 3:
        print(f"Usage: {sys.argv[0]} <boot.img> <rootfs.cpio> [output.img]")
        sys.exit(1)

    boot_img_path = sys.argv[1]
    cpio_path     = sys.argv[2]
    output_path   = sys.argv[3] if len(sys.argv) > 3 else boot_img_path

    print(f"Reading {boot_img_path} ...")
    with open(boot_img_path, "rb") as f:
        img = f.read()

    hdr, kernel, old_ramdisk, second, dt = unpack(img)
    header_raw = img[:hdr["page_size"]]

    print(f"  kernel:       {len(kernel):>10,} bytes  (preserved)")
    print(f"  old ramdisk:  {len(old_ramdisk):>10,} bytes  (KNULLI initrd, replaced)")
    print(f"  cmdline:      {hdr['cmdline']}")

    print(f"Reading {cpio_path} ...")
    with open(cpio_path, "rb") as f:
        cpio_data = f.read()
    print(f"  cpio size:    {len(cpio_data):>10,} bytes")

    print("Compressing new ramdisk (gzip) ...")
    new_ramdisk = gzip_compress(cpio_data)
    print(f"  new ramdisk:  {len(new_ramdisk):>10,} bytes  (REG-Linux initrd, gzip)")

    new_cmdline = patch_cmdline(hdr["cmdline"])
    print(f"  new cmdline:  {new_cmdline}")

    print("Repacking boot image ...")
    new_img = repack(hdr, header_raw, kernel, new_ramdisk, second, dt, new_cmdline)

    with open(output_path, "wb") as f:
        f.write(new_img)
    print(f"Written: {output_path}  ({len(new_img):,} bytes)")


if __name__ == "__main__":
    main()
