#!/usr/bin/env python3
"""
patch-env-img.py - Patch U-Boot environment variables in an Allwinner env.img.

Allwinner env.img format:
    [4 bytes CRC32 (LE)]  [1 byte flags]  [null-terminated key=value pairs ...]  [zero padding]

The CRC32 covers the env data (everything after the CRC and flags fields).

Usage:
    patch-env-img.py <env.img> key=value [key=value ...]

Example:
    patch-env-img.py partitions/env.img rdinit=/init loglevel=4
"""

import binascii
import struct
import sys


def parse_env(data):
    """Parse null-terminated key=value pairs from raw env data bytes."""
    pairs = []
    pos = 0
    while pos < len(data):
        end = data.find(b"\x00", pos)
        if end == pos:
            break
        pairs.append(data[pos:end].decode("ascii"))
        pos = end + 1
    return pairs


def main():
    if len(sys.argv) < 3:
        print(f"Usage: {sys.argv[0]} <env.img> key=value [key=value ...]")
        sys.exit(1)

    env_path = sys.argv[1]
    overrides = {}
    for arg in sys.argv[2:]:
        if "=" not in arg:
            sys.exit(f"ERROR: invalid argument '{arg}' (expected key=value)")
        k, v = arg.split("=", 1)
        overrides[k] = v

    with open(env_path, "rb") as f:
        img = f.read()

    total_size = len(img)
    crc_stored = struct.unpack_from("<I", img, 0)[0]
    flags = img[4]
    env_data = img[5:]

    pairs = parse_env(env_data)
    changed = []

    new_pairs = []
    for p in pairs:
        k = p.split("=", 1)[0]
        if k in overrides:
            new_val = f"{k}={overrides[k]}"
            if new_val != p:
                changed.append((p, new_val))
            new_pairs.append(new_val)
            del overrides[k]
        else:
            new_pairs.append(p)

    # Append any overrides for keys that didn't exist
    for k, v in overrides.items():
        new_val = f"{k}={v}"
        changed.append(("(new)", new_val))
        new_pairs.append(new_val)

    if not changed:
        print(f"patch-env-img: {env_path}: no changes needed")
        return

    # Rebuild
    env_bytes = b"\x00".join(p.encode("ascii") for p in new_pairs) + b"\x00"
    data_size = total_size - 5
    if len(env_bytes) > data_size:
        sys.exit(f"ERROR: env data too large ({len(env_bytes)} > {data_size})")
    env_bytes = env_bytes.ljust(data_size, b"\x00")

    crc = binascii.crc32(env_bytes) & 0xFFFFFFFF
    out = struct.pack("<I", crc) + bytes([flags]) + env_bytes

    with open(env_path, "wb") as f:
        f.write(out)

    for old, new in changed:
        print(f"patch-env-img: {old} -> {new}")
    print(f"patch-env-img: {env_path} updated (CRC 0x{crc:08X})")


if __name__ == "__main__":
    main()
