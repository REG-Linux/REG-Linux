# Broadcom BCM2836 (Raspberry Pi 2 / Zero 2 W) board

## Purpose

This folder captures the board-specific assets for the Broadcom BCM2836 target (Raspberry Pi 2 / Zero 2 W) used by REG-Linux. It provides the boot loader configuration, overlays, kernel configuration, and board hooks required to produce a working image for that platform.

## Supported Devices

- **Raspberry Pi 2 Model B** (BCM2836, Quad-core Cortex-A7)
- **Raspberry Pi Zero 2 W** (BCM2837, Quad-core Cortex-A53)
- **Raspberry Pi 3 Model B** (BCM2837, Quad-core Cortex-A53)
- **Raspberry Pi 3 Model B+** (BCM2837, Quad-core Cortex-A53)
- **Raspberry Pi Compute Module 3** (BCM2837)

## Boot Configuration

### Production Kernel

The kernel is configured for **production use** with the following optimizations:

- Optimized for size (`CONFIG_CC_OPTIMIZE_FOR_SIZE=y`)
- Debug features disabled
- Reduced memory footprint
- Faster boot time

See `PRODUCTION_KERNEL.md` and `CONFIG_CHANGES_SUMMARY.md` for details.

### Retroflag GPICase Support

**Default configuration**: Retroflag GPICase 2W overlay is **enabled by default** for Pi Zero 2 W.

In `boot/config.txt`:

```ini
# Enable UART for button communication
enable_uart=1

# GPICase 2W overlay (640x480 landscape)
dtoverlay=retroflag-gpicase2w
```

**For GPICase original (Pi Zero/1)**, comment the 2W overlay and enable:

```ini
#dtoverlay=retroflag-gpicase2w
dtoverlay=retroflag-gpicase
```

**For standard RPi 2/3 without GPICase**, comment both overlays:

```ini
#dtoverlay=retroflag-gpicase
#dtoverlay=retroflag-gpicase2w
```

### Configuration Files

- `boot/config.txt` - Firmware settings (kernel path, overlays, UART, DPI, VC4 KMS)
- `boot/cmdline.txt` - Kernel command line (fastboot, noswap, quiet/splash, rootwait)
- `create-boot-script.sh` - Board hook that copies firmware, kernel, device trees to `boot/boot`

## Filesystem Overlays

The `fsoverlay` directory contains root filesystem files:

### UDEV Rules (`etc/udev/rules.d/99-retroflag-input.rules`)

Configures input device permissions for GPICase buttons and DPI panel:

```udev
# Retroflag GPI Case buttons and controls
SUBSYSTEM=="input", ATTRS{name}=="retroflag*", MODE="0666", ENV{ID_INPUT_JOYSTICK}="1"

# DPI Panel events
SUBSYSTEM=="input", ATTRS{name}=="dpi-*", MODE="0666"
```

### Other Files

- `etc/modules.conf` - Forces load of `snd_seq` and `i2c_dev`
- `etc/openal/alsoft.conf` - Tunes OpenAL for Solarus engine

## Kernel Configuration

### Main Config

`linux-broadcom32-current.config` - Full kernel configuration for Linux 6.6 series

### Fragment Config

`board/reglinux/linux-defconfig-reglinux.config` - REG Linux common fragments:

- USB gadget (MTP, FunctionFS)
- HID controllers support
- File systems (SquashFS, OverlayFS, CIFS)
- CPU frequency scaling
- ZRAM support

### Production Optimizations

Kernel is built with:

- `CONFIG_CC_OPTIMIZE_FOR_SIZE=y` - Size optimization
- `# CONFIG_DEBUG_KERNEL is not set` - Debug disabled
- `# CONFIG_DEBUG_FS is not set` - DebugFS disabled
- `# CONFIG_FRAME_POINTER is not set` - No frame pointers
- `# CONFIG_DEBUG_INFO is not set` - No debug symbols

See `PRODUCTION_KERNEL.md` for complete documentation.

## Patches

### Board-Specific Patches (`patches/`)

- `duckstation-legacy/board-disable-message-OpenGL.patch` - Disables OpenGL OSD messages

### Kernel Patches (`../linux_patches/6.6/`)

- `0001-feat-add-retroflag-gpi2w-dpi-panel-for-kms-driver.patch` - GPICase 2W display support
- `0002-feat-add-piboy-dmg-panel-for-kms-driver.patch` - PiBoy DMG display support
- `0004-feat-add-retroflag-gpi-dpi-panel-for-kms-driver.patch` - GPICase original display support
- `linux-battery-quircks.patch` - Battery quirks for embedded devices
- `linux-usb-hid-atari-retrobit.patch` - Atari/Retrobat controller fixes
- `linux-usbhid-quirks.patch` - USB HID quirks
- `linux-wiimote-abs-not-hat.patch` - Wiimote axis fix

## Build Notes

### Prerequisites

- Buildroot external tree structure
- Docker for reproducible builds
- ~10GB free space for build

### Build Commands

```bash
# Build for bcm2836 target
make bcm2836-build

# Clean and rebuild
make bcm2836-dirclean && make bcm2836-build
```

### Output Images

Located in `output/bcm2836/images/`:

- `reglinux-bcm2836-*.img.gz` - Compressed SD card image
- `zImage` - Kernel image
- `.dtb` files - Device tree blobs

### Verify Production Config

```bash
# Check kernel optimization
zcat output/bcm2836/build/linux-*/.config.gz | grep "CC_OPTIMIZE"
# Expected: CONFIG_CC_OPTIMIZE_FOR_SIZE=y

# Check debug status
zcat output/bcm2836/build/linux-*/.config.gz | grep "DEBUG_KERNEL"
# Expected: # CONFIG_DEBUG_KERNEL is not set
```

## GPICase Hardware Notes

### GPICase 2W (Pi Zero 2 W)

- **Display**: 640x480 landscape, RGB666 DPI
- **Pixel Clock**: 19.2 MHz
- **Connection**: DPI interface via GPIO
- **Buttons**: UART communication (GPIO 14-15)
- **Audio**: 3.5mm jack via GPIO 18-19 (PWM)

### GPICase Original (Pi Zero/1)

- **Display**: 240x320 portrait, RGB666 DPI
- **Pixel Clock**: 6.4 MHz
- **Rotation**: 90° (software)
- **Connection**: DPI interface via GPIO
- **Buttons**: UART communication

## Troubleshooting

### GPICase Display Not Working

1. Check `boot/config.txt` has correct overlay enabled
2. Verify `enable_uart=1` is set
3. Check kernel logs: `dmesg | grep -i dpi`

### GPICase Buttons Not Working

1. Ensure UART is enabled: `enable_uart=1`
2. Check udev rules: `cat /etc/udev/rules.d/99-retroflag-input.rules`
3. Verify input device: `ls /dev/input/event*`

### Boot Issues

1. Check `boot/cmdline.txt` for correct root partition
2. Verify `boot/config.txt` has `kernel=boot/linux`
3. Check kernel logs: `dmesg | less`

## References

- **REG Linux Wiki**: https://wiki.reglinux.org
- **Raspberry Pi Documentation**: https://www.raspberrypi.org/documentation/
- **Device Tree Overlays**: https://www.raspberrypi.org/documentation/configuration/device-tree.md
- **GPICase GitHub**: https://github.com/RetroFlag/retroflag-picase

## License

The REG Linux repository is licensed GPL-2.0-or-later; see `COPYING`. A built
image is not entirely open source (REG-Station, regmsg and some vendor
firmware/drivers are proprietary) — see the README's License section.
