# REG-Linux Rockchip RK3326 Board Support

This directory contains the RK3326-specific pieces that get pulled into a REG-Linux build for handhelds such as the Odroid Go2/Go3, GameForce Chi, Batlexp G350, and other RK3326 clones.

## Layout

- `boot/` – board-specific U-Boot `boot.ini` along with variant `boot.batlexp-g350.ini`.
- `create-boot-script.sh` – invoked by REG-Linux to stage kernel, rootfs, device trees and overlays into the final `boot/` image.
- `fsoverlay/` – root-owned overlay content that gets merged into the target rootfs (init scripts and REG-Linux configgen helpers).
- `genimage.cfg` – RK3326 partition layout responsible for the VFAT boot partition, userdata EXT4, and the `reglinux.img` container that bundles IDB loader, U-Boot, Trust, boot, and userdata partitions.
- `linux_patches/` – kernel patch series applied when building the RK3326 kernel.
- `linux-rk3326-defconfig.config` – the full Linux kernel configuration used for the RK3326 builds.
- `patches/` – miscellaneous patches delivered to ConfigGen packages (e.g., `alsa-ucm-conf` and `ppsspp`).

## Build integration

`create-boot-script.sh` is sourced by REG-Linux with the usual six arguments (`HOST_DIR`, `BOARD_DIR`, `BUILD_DIR`, `BINARIES_DIR`, `TARGET_DIR`, `REGLINUX_BINARIES_DIR`). It prepares `${REGLINUX_BINARIES_DIR}/boot/` by copying the generated kernel (`Image`), rootfs artifacts (`rootfs.cpio.uboot`, `rootfs.squashfs`), modules/firmware/rescue payloads, and every RK3326 device tree blob before copying the board’s `boot.ini` variants into `boot/`. When adding new boards or DTs, extend this script accordingly.

The board-specific DTB/INI list includes:

```
rk3326-odroid-go2.dtb
rk3326-odroid-go2-v11.dtb
rk3326-odroid-go3.dtb
rk3326-gameforce-chi.dtb
rk3326-anbernic-rg351m.dtb
rk3326-anbernic-rg351v.dtb
rk3326-batlexp-g350.dtb
boot.ini
boot.batlexp-g350.ini
```

The script assumes the standard REG-Linux binary exports for `Image`, `rootfs.squashfs`, etc., so keep those names unchanged unless you adjust the board script in tandem.

## Filesystem overlay

The overlay adds:

- `etc/init.d/S32colorbuttonled` – a GameForce Chi hook that restores saved button and power LED colors at boot by invoking `system-gameforce`.
- `usr/share/reglinux/configgen/scripts/governor.sh` – ConfigGen event hook called on `gameStart`/`gameStop` to toggle the GPU/DMC governors between `performance` and ondemand profiles based on the saved `system.cpu.governor` setting.

These files are merged into the built rootfs by ConfigGen, so editing them requires re-running the REG-Linux build to pick up the overlay changes.

## Partition layout

`genimage.cfg` defines `rmboot` strategy:

1. `boot.vfat` – FAT32 partition labeled `REGLINUX`, ~2 GiB, mounted as `/boot`.
2. `userdata.ext4` – EXT4 partition labeled `SHARE`, 256 MiB, mounted at `/userdata` for persistent saves and configs.
3. `reglinux.img` – large container that embeds `idbloader.img`, `uboot.img`, `trust.img`, the FAT boot partition, and the userdata partition. It follows the Rockchip expectations for flashing the complete image to the device.

Adjust partition sizes here if you need a different boot/userdata ratio; `genimage` will recreate the image from scratch.

## Kernel configuration and patches

`linux-rk3326-defconfig.config` contains the generated kernel configuration (Linux 6.12.30) tailored for RK3326 handheld hardware. Use it as the defconfig when building the kernel for this board.

`linux_patches/` holds the patch series applied on top of the kernel. Highlights include:

- input/gamepad support (`gameforce-joypad`, generic joypad drivers, RGB20S/XU10 patches, Odroid Go2/Go3 patches)
- Rockchip-specific DT offsets and display fixes (`gameforce-dts`, `panel-r36s`, `batlexp-g350-dts`, etc.)
- RK817 battery and RTC handling (`rk817-*.patch`, `rocknix` series)
- DMC driver tuning and GPU governor tweaks (`dmc-driver`, `dmc-fdi-devfreq-px30`)
- Wi-Fi/input driver updates for esp8089 and other clones

Maintain this list whenever adding or removing patches; the scripts expect them under `linux_patches/` when building the kernel.

## ConfigGen package tweaks

The `patches/` subtree carries minor fixes that REG-Linux applies to ConfigGen packages:

- `alsa-ucm-conf/000-PlaybackVolume.patch` – audio volume adjustments.
- `ppsspp/board-maxwindow.patch` – PWM and UX tweaks for the PPSSPP emulator.

Add new patches here when you need board-specific tweaks for ConfigGen-managed packages.

## Notes

- Keep the `boot/*.ini` files in sync with the expected boot script entries when supporting new RK3326 clones.
- Update the governor and LED scripts in `fsoverlay/` only after testing on actual hardware, since mistakes can leave the device unresponsive.
- Run `genimage` via the REG-Linux build system to regen `reglinux.img` after changing `genimage.cfg`, `boot.ini`, or overlay content.
