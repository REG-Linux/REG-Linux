# REG Linux · Amlogic Board Support Packs

`board/amlogic/` contains the Buildroot support packs that power REG Linux on every Amlogic SoC family. Each subdirectory holds the boot assets, overlays, kernel configuration fragments, patch queues, and post-image helpers described in its own `README.md`. This top-level summary points to the packs, explains the shared resources, and captures the most important build commands.

## Shared resources

- `fsoverlay/`, `linux-meson64-current.config`, `linux_patches/`, and `patches/` provide the overlays, kernel fragments, and package fixes that are reused by many packs. Each board-level README clarifies which of those directories it layers in.
- Per-board directories follow the same structure: `create-boot-script.sh`, a `boot/` payload (scripts, extlinux/uEnv files, logos), `genimage.cfg`, and, when needed, a `build-uboot.sh` helper. The pack README also records which DTBs are staged, how signed U-Boot blobs are handled, and any extra firmware or package tweaks.
- Build integrations live under `configs/`: e.g., `configs/reglinux-s905.board`, `configs/reglinux-s905gen2.board`, etc., define the defconfig, kernel DTBs, overlay order, and toolchain options referenced in each README.

## Support pack matrix

| Pack | Directory | SoC / Boards | Highlights | Build command & output |
| --- | --- | --- | --- | --- |
| S905 / S905X / S905D | `s905/` | Khadas VIM1, Libretech Le Potato (v1/v2), Odroid-C2, NanoPi K2, Minix NEO U1, Nexbox P201, generic S905 TV boxes | Mainline U-Boot builds (2025.01) plus LibreELEC FIP, shared `fsoverlay` helpers for ALSA+temps, XT kits for PPSSPP/Mupen64, and a multi-DTB “s905-tvbox” image that keeps the kernel as `uImage`/`uInitrd`. | `make s905-build` → `output/s905/images/reglinux/images/<board>/` |
| S905 Gen2 (GXM / G12A) | `s905gen2/` | Khadas VIM2 (S912), Radxa Zero (G12A/S905Y2) | Adds Broadcom 43456 firmware/NVRAM overlay, Gen2-specific kernel fragment, shared U-Boot patches, and packaged Radxa U-Boot blob. | `make s905gen2-build` → `output/s905gen2/images/reglinux/images/<board>/` |
| S905 Gen3 (SM1 / S905X3) | `s905gen3/` | Banana Pi M5, Khadas VIM3L, Odroid C4, generic S905X3 TV boxes (H96/X96/A95X clones) | Keys on SM1-specific kernel Kconfig fragments and X96 Max Plus DTB patches, TV-box helper that ships `uEnv.txt`/`boot.ini` plus AML scripts, and LibreELEC-style U-Boot fips for mainline builds. | `make s905gen3-build` → `output/s905gen3/images/reglinux/images/<board>/` |
| S9 Gen4 (S905Y4) | `s9gen4/` | Khadas VIM1S | Vendor kernel (Khadas 5.15 tree) + signed VIM1S U-Boot, Dracut initramfs recipe, extensive `linux_patches/` for audio/display, and overlay scripts for Plymouth/fan/firmware. | `make s9gen4-build` → `output/s9gen4/images/reglinux/images/khadas-vim1s/` |
| S922X / A311D | `s922x/` | Khadas VIM3, Banana Pi M2S, Beelink GT-King/Pro, Odroid N2/N2+/N2L, Radxa Zero2/Pro, Odroid Go Ultra | Massive patch queue for G12B/A311D quirks, overlay scripts for HDMI/audio/overclocking, Odroid-Go-Ultra U-Boot patches/resources, and U-Boot builds for every board (2024.01). | `make s922x-build` → `output/s922x/images/reglinux/images/<board>/` |
| A3 Gen2 (A311D2) | `a3gen2/` | Khadas VIM4 (A311D2 “A3 Gen2”) | Khadas vendor kernel/5.15 config, signed VIM4 U-Boot blob, dracut recipe, overlay scripts for fan/video firmware, and package/kernel patches for Realtek Wi-Fi, Vulkan, and Wayland. | `make a3gen2-build` → `output/a3gen2/images/reglinux/images/khadas-vim4/` |
| S812 / Meson8 | `s812/` | Tronsmart MXIII, MXIII+, Minix Neo X8, M8S family, WeTek Core, Tronsmart S82 | Legacy U-Boot scripts (`aml_autoscript`, `s805_autoscript`), `uImage` + `uInitrd` packaging, huge patch queue to resurrect HDMI/CVBS, NAND, remote, and Cirrus audio for the Meson8/Meson8m2 family. | `make s812-build` → `output/s812/images/reglinux/images/s812/reglinux.img` |

Each row links to the full `board/amlogic/<pack>/README.md` for per-board DTB lists, overlays, and extension notes.

## Extending support packs

Contributions typically follow the same steps across the README files:

1. Copy the closest `board/amlogic/<pack>/<board>/` directory and adjust `create-boot-script.sh`, the boot config (`extlinux.conf`, `uEnv.txt`, `boot.ini`), and `genimage.cfg` as needed (new DTB, partition sizes, ALSA/serial tweaks).
2. Add the new DTB to the corresponding Buildroot config (`configs/reglinux-<pack>.board`) so the kernel, overlays, and firmware know about the hardware.
3. Drop any extra firmware, scripts, or kernel fragments into the pack’s `fsoverlay/`, `linux-defconfig-fragment.config`, or `linux_patches/`; keep package fixes in `patches/`.
4. Document your work inside the pack’s README so the next maintainer understands the boards, quirks, and build hooks.

Refer to each pack’s `README.md` for detailed build integration notes, patch descriptions, and board-specific instructions.
