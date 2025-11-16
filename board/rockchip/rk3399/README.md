# Rockchip RK3399 board support
This folder gathers the device-specific boot helpers, overlays, device trees, kernel configuration, and patch queues that REG-Linux applies to Rockchip RK3399-based hardware.

## Board directories
Each board directory mirrors the layout expected by the build/release scripts:

- `*/boot/` holds an `extlinux.conf` snippet that describes the kernel, initramfs, and dtb to boot on that board.
- `create-boot-script.sh` wraps `extlinux.conf` with `mkimage` so you can drop an up-to-date `boot.scr` on the boot partition without editing binary blobs.
- `genimage.cfg` describes the partition layout and files that `genimage` should assemble when creating SD cards or eMMC images for the board.

The current boards in this tree are:

- `anbernic-rg552`
- `hugsun-x99`
- `nanopi-m4v2`
- `orangepi-4-lts`
- `orangepi-800`
- `rock960`
- `rock-pi-4`
- `rockpro64`
- `tinkerboard2`

## Device trees
`dts/` contains the REG-Linux device tree sources for the boards that need local tweaks. The collection currently includes:

- `rk3399-anbernic-rg552.dts`
- `rk3399-nanopi-m4v2.dts`
- `rk3399-orangepi-4-lts.dts`
- `rk3399-orangepi-800.dts`
- `rk3399-tinker-2.dts`

Drop additional `.dts` files here when you need to diverge from the upstream Rockchip tree; the build system picks up every source in this directory when assembling the DTB bundle.

## Filesystem overlay
`fsoverlay/` is mounted on top of a root filesystem after `genimage` lays down the base. Its tree contains:

- `etc/init.d/` to install runtime helpers such as fan control, HDMI detection, Wi-Fi watchdogs, and HDMI reloading.
- `lib/firmware/` with Bluetooth firmware blobs and the `uwe5622` firmware chain for the USB Wi-Fi dongle that REG ships with RK3399 systems.
- `usr/bin/` utilities like `batocera-check-hdmi`, `cputemp`, and `gputemp` that run on the target system.
- `usr/share/alsa/cards/` card definitions that wire the onboard codecs into ALSA.

Customize this overlay (adding or removing files) before running the image builder to alter the runtime configuration without touching the upstream rootfs.

## Kernel configuration
`linux-defconfig.config` is the exported `.config` from the 6.12.21 kernel build used by REG-Linux. It is the definitive starting point for the RK3399 kernel: rerun `make defconfig` with this file (for example, by copying it to `arch/arm64/configs`) before compiling the kernel so that all RK3399-specific features and drivers are enabled.

## Kernel patch queues
`linux_patches/` carries a broad set of `.patch` files that cover:

- board-specific fixes (`board-rockpro64-*`, `board-nanopi-*`, `board-orangepi-*`, etc.).
- general RK3399 feature work (USB PHY, PCIe fixes, HDMI timing, fan regulators).
- driver updates (V4L2/RKVDEC, regulator drivers, pl330 DMA improvements).
- firmware and Wi-Fi tweaks (uwe5622 and related chips).

Apply these patches on top of the kernel before building (for example, by feeding them to `scripts/patch-kernel.sh`). The naming convention documents the main purpose or subsystem affected, so you can pick only the series you need.

## Auxiliary patches
`patches/` hosts additional patch trees for other third-party components that need changes when paired with the RK3399 boards:

- `atf/` – Rockchip Arm Trusted Firmware patches.
- `libdrm/` – DRM layer adjustments.
- `moonlight-embedded/` and `ppsspp/` – application-level tweaks for Batocera/REG targets.

Keep these patches in sync with their respective third-party trees and reapply them when you update the binaries in the board support package.

## Working with this tree
1. Choose the board directory that matches the hardware you are targeting.
2. Update `boot/extlinux.conf` if you need kernel/initrd changes, then regenerate `boot.scr` with `./create-boot-script.sh` from the same directory.
3. Feed `genimage.cfg` into `genimage` (calls to `buildroot` already know how to do this) to build the complete SD/eMMC image.
4. Apply the kernel configuration and patch series from `linux-defconfig.config` and `linux_patches/` before building the kernel for the target board.
5. Drop additional files, helpers, or firmware into `fsoverlay/` to tweak the filesystem without rebuilding the whole image.

If you add new RK3399 boards, mirror the directory layout above so the build scripts can consume them automatically.
