# RK3128 Board Support (WIP)

> **Warning:** this directory contains a work-in-progress port of **mainline Linux** for Rockchip RK3128 boards. No display support exists yet and the images are only meant for developers experimenting with REG-Linux; do not ship them to end users.

## Status
- Built against the `linux-defconfig.config` for Linux 6.10.0-rc2 with the `-reglinux` suffix; `linux-defconfig-fragment.config` holds the bits that need tweaking for our board (e.g., UART consoles, kernel debugging, and modules that ship with REG-Linux).
- Kernel patches in `linux_patches/` keep the various RK3128 DTS and USB quirks in sync with the rest of the stack. The patches shown here are already part of the `make` flow, but you can edit or rebase them when upstream changes land.
- There is no display driver wired up yet—existing test boots rely on UART for debugging and `earlycon=uart8250,mmio32,0x20060000`.

## Layout

- **`dts/`** – device tree sources and includes for the RK3128 core plus the derivatives we target (`rk3128.dtsi`, `rk3128x.dtsi`, the EVB/box files, and RK3128-dram timing definitions). Board-specific DTS files include Powkiddy A12/A13 variants, PS5000/PS7000 tablets, WX8, FirePrime, and XPI hardware.
- **`fsoverlay/`** – overlay files copied onto the target filesystem via REG-Linux. They add Udev rules (headset hotplug, drm permissions, Wi-Fi/BT reset scripts), a `governor.sh` helper under `usr/share/reglinux`, PipeWire hooks, and helper binaries (`headset-hotplug.sh`, `cputemp`). Adjust these if you need different runtime configuration.
- **`linux_patches/`** – additional patch set applied on top of mainline Linux:
  - `00-custom-dts.patch` stitches the REG-Linux device tree fragments together.
  - `01-ps5000-dts.patch` and `02-ps7000-dts.patch` carry board-specific tweaks (display timings, button mappings, regulators).
  - `09-linux-usbhid-quircks.patch` & `10-linux-wiimote-abs-not-hat.patch` are hardware quirks needed for legacy input devices such as Wiimote/PS-style controllers.
  - `uvc-bandwidth_cap_param-for-sinden.patch` relaxes the USB video bandwidth cap for some capture devices.
- **`patches/`** – per-subsystem patches consumed by the REG-Linux build:
  - `uboot-*` directories hold the `gcc13` fixes used when building U-Boot for Powkiddy A13, PS5000, and PS7000.
  - `reglinux-emulationstation`, `ppsspp`, `libcec` contain additional fixes so those components compile cleanly with the RK3128 toolchain and device quirks.

## Board targets

Each subdirectory (`powkiddy-a13`, `ps5000`, `ps7000`, `xpi3128`) mirrors the REG-Linux board layout: `genimage.cfg` describes the partition map of the boot image, `create-boot-script.sh` is invoked by the REG-Linux build system to copy `zImage`, `initrd.lz4`/`rootfs` assets, and DTBs into the `boot` tree, and `boot/extlinux.conf` defines the boot loader entry(s) plus the enforced console/kernel arguments.

- `powkiddy-a13/boot/extlinux.conf` includes multiple commented `FDT` choices with the production FDT for the Powkiddy A12/A13 screens and a temporary test entry (`rk3128-xpi-3128.dtb`).
- `ps5000` and `ps7000` use their respective DTBs (`rk3128-ps5000.dtb`, `rk3128-ps7000.dtb`) and share `earlycon=uart8250...` arguments; you can uncomment the EVB/XPI DTB entries to experiment with other board setups.
- `xpi3128` currently boots with `rk3128-xpi-3128.dtb` and exposes the same UART/console flags.

## Build notes

- REG-Linux already wires this board tree into the top-level build—`make <board>` (e.g., `make powkiddy-a13`) should pick up the correct DTBs, patches, overlays, and boot scripts.
- When the build copies artifacts into `REGLINUX_BINARIES_DIR`, `create-boot-script.sh` guarantees the right layout under `boot/boot` (Linux image, modules/firmware updates, `reglinux.update`, etc.) and under `boot/extlinux` (GRUB-style configuration). `genimage.cfg` ensures genimage writes the right partition table for each board.
- If you need to change the kernel configuration, edit `linux-defconfig.config` (after running `make defconfig`) and/or `linux-defconfig-fragment.config`, then regenerate the config before building.

## Developer guidance

- Testing is done via UART; if you need display support, you will have to enable the appropriate display controller nodes in the DTS and port a framebuffer driver—this port does not ship with one yet.
- Keep the RK3128 DTB changes in sync with the patches under `linux_patches/`; rebuild the kernel when you alter those files so the patched DTS files regenerate.
- Be conservative when editing the overlays: the current `udev` rules assume the headphone pin and PWM fan setup used by REG-Linux phones/tablets without touching the LCD stack.
