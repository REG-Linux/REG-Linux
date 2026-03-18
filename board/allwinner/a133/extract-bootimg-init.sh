#!/bin/bash
# Extract and display the init script from the boot.img blob on the SD card
# Usage: sudo bash extract-bootimg-init.sh [/dev/sdX]
DEV="${1:-/dev/sda}"

python3 -c "
import struct, math, gzip

with open('${DEV}1', 'rb') as f:
    img = f.read(20*1024*1024)

if img[:8] != b'ANDROID!':
    print('ERROR: not an Android boot image')
    exit(1)

kernel_size = struct.unpack_from('<I', img, 8)[0]
ramdisk_size = struct.unpack_from('<I', img, 16)[0]
page_size = struct.unpack_from('<I', img, 36)[0]

kernel_off = page_size
ramdisk_off = kernel_off + math.ceil(kernel_size / page_size) * page_size

ramdisk_gz = img[ramdisk_off:ramdisk_off + ramdisk_size]
print(f'boot.img ramdisk: {ramdisk_size} bytes (gzip)')

cpio = gzip.decompress(ramdisk_gz)
print(f'CPIO uncompressed: {len(cpio)} bytes')

# Extract init from newc cpio
pos = 0
found = False
while pos < len(cpio) - 6:
    if cpio[pos:pos+6] != b'070701':
        pos += 1
        continue
    namesize = int(cpio[pos+94:pos+102], 16)
    filesize = int(cpio[pos+54:pos+62], 16)
    name_start = pos + 110
    name = cpio[name_start:name_start+namesize-1].decode('ascii','replace')
    data_start = (name_start + namesize + 3) & ~3
    if name == 'init':
        init_data = cpio[data_start:data_start+filesize]
        print(f'\\n/init from boot.img: {filesize} bytes')
        print('=' * 60)
        print(init_data.decode('ascii','replace'))
        print('=' * 60)

        # Quick checks
        text = init_data.decode('ascii','replace')
        print()
        checks = [
            ('DEBUGLOG',                'Has debug logging'),
            ('wdt_kick',                'Has manual watchdog kicks'),
            ('watchdog -t',             'Has watchdog daemon'),
            ('devtmpfs',                'Has devtmpfs mount'),
            ('LABEL=REGLINUX',          'Uses LABEL=REGLINUX'),
            ('do_root',                 'Has do_root function'),
            ('|| true',                 'Has non-fatal modules mount'),
            ('continuing without',      'Has continuing-without-modules msg'),
        ]
        for pattern, desc in checks:
            status = 'OK' if pattern in text else 'MISSING'
            print(f'  [{status}] {desc} ({pattern})')
        found = True
        break
    data_end = data_start + filesize
    pos = (data_end + 3) & ~3

if not found:
    print('ERROR: /init not found in cpio!')
"
