# RK3288 Board Support

> **Warning:** this directory hosts the Rockchip RK3288 board definitions that the REG-Linux build system ships into the final images. The images are functional for MiQi phones and the Tinker Board S but are still tuned for developers—display/graphics tweaks, device tree updates, and driver patches are still in flux.

## Status
- `linux-defconfig.config` pins Linux 6.6.40 with the `-reglinux` suffix (see `CONFIG_LOCALVERSION="-reglinux"` near the top) and enables features such as LZ4-compressed kernels plus the usual UART/console, thermal, and debugging helpers we rely on.
- The `linux_patches/` directory keeps the RK3288 DTS fragments, power/OPP tables, SDMMC/SPI pinctrls, V4L2 accelerators, Broadcom/Realtek wireless quirks, and other Rockchip-specific fixes in sync. Key patches include:
  - `linux-2102-*` through `linux-2117-*` for missing SPI2 pinctrls, SDIO/Wi‑Fi/Bluetooth pin wiring, I2C/SPI definitions, CPU/GPU voltage tables, thermal-zone layouts, and MMC/SPI driver fixes that the RK3288 revisions need.
  - `linux-2000-*`/`linux-2001-*` and `linux-1001-*`/`linux-1002-*` for the V4L2 rkvdec/iep stacks used by video/streaming components.
  - `linux-2120-brcmfmac` and `linux-2118-workaround-broadcom-bt-serdev` for Wi‑Fi and BT firmware handling, plus ` linux-RK3288-1.8GHz-and-boost.patch`, `linux-RK3288-MiQi-*`, and `linux-rockchip-Enable-4K-60Hz-*` for CPU/GPU performance tuning, display timing, and other SoC quirks.
  - `uvc-bandwidth_cap_param-for-sinden.patch` leaves room for USB video capture devices that surf via Sinden inputs.
- `patches/` holds downstream tweaks that are packaged into REG-Linux:
  - `patches/bluez5_utils-5.47/bluez5_utils-add-rtl-bt.patch` injects a Realtek `hciattach_rtk_h5` helper so the board can attach RTL Bluetooth modules without manual intervention.
  - `patches/dxx-rebirth/001-fix-32bit-werror-useless-cast.patch` removes the unnecessary unsigned cast in `similar/main/songs.cpp`, letting `dxx-rebirth` survive `-Werror=useless-cast`.
  - `patches/moonlight-embedded/001-disable-rockchip-rga-mpp.patch` comments out the Rockchip backend in `CMakeLists.txt`, which avoids the Rockchip RGA dependency that Moonlight no longer ships.
- `fsoverlay/` overlays get copied into the target rootfs. They currently add temperature helpers (`fsoverlay/usr/bin/cputemp` and `fsoverlay/usr/bin/gputemp`) and ALSA card configurations tailored for the rk3288 audio routes (`fsoverlay/usr/share/alsa/cards/{Analog.conf,simple-card.conf,SPDIF.conf}`).

## Layout
- **`miqi/`** and **`tinkerboard/`** mirror the REG-Linux board layout: `genimage.cfg` defines the partition map, `create-boot-script.sh` arranges the boot tree under `boot/boot` and `boot/extlinux`, and `boot/extlinux.conf` is the default loader entry that points to `/boot/linux`, the appropriate DTB, and the initrd.
- **`linux-defconfig.config`** is the canonical kernel config for RK3288 builds; run `make defconfig` with your kernel tree to update it and commit the diff if you add features.
- **`linux_patches/`** is layered on top of every RK3288 kernel build. Rebase those patches when upstream DTS/init, V4L2, or multimedia subsystems change.
- **`patches/`** contains package-specific patches and is staged by the REG-Linux build to keep the BlueZ utilities, Moonlight, and DXX-Rebirth trees usable on RK3288 hardware.
- **`fsoverlay/`** overlays are copied verbatim onto the target root filesystem and should be edited if you want different temp helpers, ALSA card definitions, or other host-level defaults.

## Board targets

- **MiQi**
  - `miqi/create-boot-script.sh` copies `zImage`, `initrd.lz4`, module/firmware/rescue branches, and `rk3288-miqi.dtb` into `REGLINUX_BINARIES_DIR/boot/boot`, then drops `miqi/boot/extlinux.conf` into `REGLINUX_BINARIES_DIR/boot/extlinux`.
  - `miqi/genimage.cfg` writes a 2 GiB FAT boot image plus a 256 MiB `userdata.ext4` share partition, then produces `reglinux.img` with the MiQi `idbloader.img`/`u-boot.img` (from `uboot-multiboard/miqi-rk3288`) plus a VFAT `boot.vfat` partition and the `userdata` ext4 volume.
  - `miqi/boot/extlinux.conf` points at `/boot/linux` and `/boot/rk3288-miqi.dtb` with `initrd=/boot/initrd.lz4 label=REGLINUX rootwait quiet splash console=uart8250,mmio32,0xff690000`.

- **Tinker Board S**
  - `tinkerboard/create-boot-script.sh` is nearly identical to the MiQi variant but copies `rk3288-tinker.dtb`/`rk3288-tinker-s.dtb`, reflecting the Asus Tinker board families, and installs `tinkerboard/boot/extlinux.conf`.
  - `tinkerboard/genimage.cfg` shares the same partition layout (boot VFAT, userdata ext4, `reglinux.img`) but prepends the Tinker-specific `idbloader.img`/`u-boot.img` from `uboot-multiboard/tinker-s-rk3288`.
  - `tinkerboard/boot/extlinux.conf` adds a `DEFAULT reg.linux` entry that also points at `/boot/linux`, `/boot/rk3288-tinker.dtb`, and the same initrd/console arguments.

## Build notes
- The RK3288 tree is wired into `make <board>` (for example `make miqi` or `make tinkerboard`) so the build system pulls the right DTBs, overlays, patches, and boot scripts.
- `create-boot-script.sh` scripts guarantee that `REGLINUX_BINARIES_DIR/boot/boot` holds the kernel, initrd, squashfs update blobs, modules, firmware, and rescue archives, while `boot/extlinux` gets the loader entry used by the firmware.
- `genimage.cfg` files orchestrate `genimage` so that `reglinux.img` contains both the Rockchip bootloaders and a VFAT boot partition plus a small userdata slice. Update the offsets or partition sizes in that file if you need more space.
- When you tweak drivers or features, edit `linux-defconfig.config` (or the corresponding fragment) and regenerate before building so the config stays in sync with the patches.

## Developer guidance
- Keep device tree tweaks in `linux_patches/` aligned with upstream Rockchip trees before bumping the kernel—these patches are applied in series, so rebasing small DTS commits avoids conflicts.
- Overlay changes are copied straight onto the target rootfs; adjust `fsoverlay/usr/bin/cputemp`/`gputemp` or the ALSA cards only if you need different thermal helpers or voice routes.
- `patches/bluez5_utils-5.47/bluez5_utils-add-rtl-bt.patch` is required for Realtek BT controllers; if you ship new Bluetooth hardware, update the firmware names/paths it writes to `/lib/firmware/rtl_bt`.
- The `moonlight-embedded` and `dxx-rebirth` patches in `patches/` keep those applications building, so review them whenever the underlying package version changes.
