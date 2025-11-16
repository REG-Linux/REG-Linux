# Rockchip board support

This directory groups the REG-Linux board support for every Rockchip family we ship. Each `rk*` directory holds the kernel configuration/patches, `create-boot-script.sh`, `genimage.cfg`, `boot/extlinux.conf`, and any overlays or helper scripts for the devices based on that SoC. The sibling `fsoverlay/` and `patches/` directories provide shared overlays and userland patches that are layered on top of whichever board is being built.

## RK3128 (work in progress)

- Linux 6.10.0-rc2 with `linux-defconfig.config`/`linux-defconfig-fragment.config`, patched DTS fragments, USB quirks, and UART-only boots for PoKiddy A12/A13, PS5000/PS7000, WX8, FirePrime, and XPI hardware.
- `dts/`, `fsoverlay/`, and `linux_patches/` contain the device trees, board overlays (udev rules, governor scripts, PipeWire hooks), and patchset that stitch the RK3128 trees together; no display stack yet.
- Each subdirectory (e.g., `powkiddy-a13`, `ps5000`, `xpi3128`) mirrors the REG-Linux board layout so the build scripts can stage kernels, DTBs, and boot scripts/`extlinux.conf` entries as usual.

## RK3288

- Kernel 6.6.40 (`linux-defconfig.config` with `-reglinux` localversion) augmented with Rockchip and RK3288-specific patches (SDMMC/SPI pinctrls, V4L2 stacks, Broadcom/Realtek wireless tweaks, display/boost helpers, USB video tweaks).
- Downstream `patches/` keep BlueZ helpers, Moonlight, and DXX-Rebirth compatible; `fsoverlay/` installs temperature helpers and the ALSA card definitions tailored for MiQi/Tinker Board S audio paths.
- Boards `miqi/` and `tinkerboard/` each supply `create-boot-script.sh`, `genimage.cfg`, and `boot/extlinux.conf`, ensuring the kernel/initrd/DTB are staged and `grub`/`extlinux` entries match the Rockchip bootloaders the images ship with.

## RK3326

- Targets handhelds such as the Odroid Go2/Go3, GameForce Chi, Batlexp G350, and other RK3326 clones, using `linux-rk3326-defconfig.config` (Linux 6.12.30) plus the `linux_patches/` series for joypads, DT offsets, battery/RTC, DMC/GPU governor, and Wi-Fi/input drivers.
- `create-boot-script.sh` copies the REG-Linux binaries into `REGLINUX_BINARIES_DIR` (kernel, rootfs, modules, firmware) and drops the device trees plus `boot.ini` variants (`boot.batlexp-g350.ini`) into the boot partition.
- Overlay (`fsoverlay/`) injects LED/color restore scripts and ConfigGen governor hooks.
- `genimage.cfg` defines the FAT32 boot, EXT4 userdata, and `reglinux.img` container that bundles every RK3326-specific DTB/bootloader; update partition sizes if you need different ratios.
- Package patches (`patches/alsa-ucm-conf`, `patches/ppsspp`) hold ConfigGen tweeks for audio and PPSSPP.

## RK3328

- `linux-rk3328-defconfig.config` plus a collection of kernel patches covering Rockchip helpers, DRM/V4L2, temperature fixes, USB video bandwidth, and LibreELEC-aligned adjustments.
- Two board directories (`renegade/`, `rock64/`) each provide `create-boot-script.sh`, `genimage.cfg`, `boot/extlinux.conf`, and board-specific DTBs/bootloader binaries (`rk3328-roc-cc.dtb`, `rk3328-rock64.dtb`).
- `fsoverlay/` adds monitoring helpers and ALSA cards used across RK3328 images; `patches/` is reserved for long-term board-specific tweaks.

## RK3399

- Covers multiple boards (`anbernic-rg552`, `hugsun-x99`, `nanopi-m4v2`, `orangepi-4-lts`, `orangepi-800`, `rock960`, `rock-pi-4`, `rockpro64`, `tinkerboard2`), all of which expose `boot/extlinux.conf`, `create-boot-script.sh`, and `genimage.cfg`.
- `dts/` holds RK3399-specific sources for boards requiring local tweaks.
- Overlay (`fsoverlay/`) installs init scripts (fan control, HDMI detection, Wi-Fi watchdogs), firmware blobs, and helper binaries (`batocera-check-hdmi`, `cputemp`, ALSA card definitions).
- `linux-defconfig.config` (Linux 6.12.21) plus `linux_patches/` and `patches/` collections keep kernel drivers, V4L2, firmware, and third-party packages aligned with the hardware requirements.

## RK3568

- Hosts board directories (`anbernic-rgxx3`, `firefly-station-m2/p2`, `odroid-m1/m1s`, `rock-3a/3c`) whose `create-boot-script.sh` scripts gather kernels, firmware, DTBs, extlinux configs, boot logos, and helper files into the REG-Linux binaries tree.
- Some boards use `build-uboot.sh` to download/patch/build U-Boot 2025.01, while others copy prebuilt `idbloader.img`/`uboot.img`.
- Shared `fsoverlay/` provides temperature reporters and ALSA cards, while `linux-defconfig.config` (Linux 6.6.40) and `linux_patches/` adjust input/power handling plus RK817 tweaks. U-Boot patches live under `patches/uboot/`.
- `genimage.cfg` files describe the required partition layout so `genimage` can package boot/extlinux images consistently.

## RK3588

- Central `linux-defconfig.config` targets Linux 6.1.118 (Buildroot 2025.02.7) with `CONFIG_LOCALVERSION=-reglinux`; `linux_patches/` cover battery, power-off, Radxa wireless, Panthor support, and streaming UVC tweaks.
- `patches/` bundles package fixes (Moonlight, SDL2/OpenGLES, RTL8821CU, Vita3K, PPSSPP, XInput/xpad) plus U-Boot patches that add HDMI nodes and other upstream fixes; `dts/` holds the GameForce Ace source.
- Shared `fsoverlay/` injects fan/audio scripts, runtime helpers, ALSA definitions, Bluetooth helper binaries, and Mali firmware.
- Each board (bananapi-m7, firefly-station-m3, gameforce-ace, indiedroid-nova, khadas-edge-2, mekotronics-r58, orangepi-5/e5b/e5-plus, quartzpro64, rock-5a/b/c) ships `create-boot-script.sh`, `genimage.cfg`, and `boot/extlinux.conf`; some also build U-Boot in-tree (see board table in `rk3588/README.md`).
- `genimage.cfg` definitions produce a 3 GiB boot FAT32 partition plus a 256 MiB userdata slice and embed `u-boot-rockchip.bin` into the GPT image for flashing.
