# REG Linux System Architecture

REG Linux (Retro Emulation Gaming Linux) is an immutable Buildroot-based operating system that targets ARM, AArch64, RISC-V, MIPS32el, and x86_64 handhelds, SBCs, and mini-PCs. This document describes how the operating system is assembled and behaves at runtime. It focuses on the system architecture rather than the repository layout.

## 1. Design Principles

- **Immutable core** – The playable system ships as a compressed SquashFS image that is never modified in-place. Updates replace whole images, not individual packages.
- **Deterministic builds** – Buildroot, a pinned toolchain, and per-board defconfigs keep firmware reproducible. Docker-based tooling ensures host independence.
- **Configurable peripherals** – GPU selection, display routing, controller quirks, and case-specific daemons are encoded as Buildroot packages and board overlays.
- **Split state** – `/` is read-only, `/userdata` holds everything user-writable, and `/boot` is the minimal vendor-friendly partition that also carries upgrades.
- **Message-driven services** – A brand-new, custom-made IPC-based system daemon managind and exposing hardware control through different system parts.

## 2. Build & Packaging Pipeline

### 2.1 Buildroot external tree

- Every target inherits `configs/reglinux-board.common` or `configs/reglinux-board.mini`, which pulls BusyBox, GNU userland, SquashFS tooling, MTP responder, SDL2/SDL3, libv4l, and the reglinux system packages (`BR2_PACKAGE_REGLINUX_SYSTEM`, `BR2_PACKAGE_REGLINUX_ALL_SYSTEMS`).
- Per-board `.board` files (e.g. `configs/reglinux-rk3588.board`) include a toolchain fragment (`toolchain-gcc14-glibc.common`) and define SoC-specific optimizations, DTs, patch directories, overlays, and image recipes.
- `BR2_TARGET_REGLINUX_IMAGES` (declared in `package/system/reglinux-system/Config.in.targets`) collects the list of hardware variants that reuse the same binary build. The post-image hook iterates this list to emit per-device SD-card images.

### 2.2 Toolchain and kernel

- Toolchains default to GCC 14 + glibc with `-O3`, LTO, OpenMP, Graphite, and gold linker support (`configs/toolchain-gcc14-glibc.common`).
- Linux is built per board, but all kernels share a fragment (`board/reglinux/linux-defconfig-reglinux.config`) that enables the HID stack, overlayfs, SquashFS LZ4/Zstd support, CIFS/KSmbd server, Perf, and dozens of controller drivers.
- Kernel sources, additional config fragments, and DTS selections are declared in each `.board` file. Vendor-specific patches live under `board/<vendor>/<soc>/patches` while global tweaks live under `board/reglinux/linux_patches`.

### 2.3 Build orchestration

- The root `Makefile` drives Buildroot through Docker to keep host dependencies minimal. Targets such as `make rk3588-build` create `output/rk3588/` and execute Buildroot with `BR2_EXTERNAL=/build`.
- Common options (`PARALLEL_BUILD`, `DEBUG_BUILD`, etc.) are turned into Buildroot symbols by appending their values to the generated defconfig (`configs/createDefconfig.sh`).
- Downloads are shared through `dl/`, artifacts live under `output/<target>/`, and `buildroot-ccache/` caches compiler outputs across builds.

### 2.4 Post-build & post-image hooks

- `board/scripts/post-build-script.sh` runs inside Buildroot after the root filesystem is staged. It:
  - Packages `/lib/modules` and `/lib/firmware` as SquashFS archives (`modules.update`, `firmware.update`) via `board/reglinux/scripts/package-*.sh`.
  - Places root’s home in `/userdata/system`, re-points Dropbear, EmulationStation, iptables, etc. to `/userdata`.
  - Reorders init scripts (earlier dbus/network, later rngd/triggerhappy) and strips unused binaries or tests.
  - Generates `/usr/share/reglinux/system.version`, `system.arch`, and the `datainit.squashfs` bundle that seeds `/userdata`.
- `board/scripts/post-image-script.sh` consumes the staged filesystem and:
  - Invokes each board’s `create-boot-script.sh`, which copies `Image`, `rootfs.cpio.lz4`, `rootfs.squashfs` (renamed to `reglinux.update`), module/firmware/rescue updates, DTBs, and configuration files into `boot/boot/`.
  - Runs `genimage` per board to emit `boot.vfat`, `userdata.ext4`, and a final `reglinux-<target>-<board>-YY.MM-date.img.gz`. VFAT UUIDs are randomized per build and injected into bootloaders.
  - Produces `MD5SUMS`/`SHA256SUMS` and copies `system.version` plus the per-build system report under `binaires/reglinux/`.

## 3. Boot Flow & Storage Layout

REG Linux images ship as GPT disks with a vendor-friendly VFAT boot partition and a writable userdata partition. The boot slice carries bootloaders, kernel, initramfs, immutable SquashFS payloads, firmware/module archives, and the rescue/overlay artifacts needed for system recovery. At power-on the initramfs simply mounts that partition, applies any update packages it finds, assembles the read-only root using the SquashFS image plus an in-RAM overlay (optionally hydrated from a saved overlay file), then hands execution to BusyBox init once `/lib/firmware`, `/lib/modules`, and `/boot/system-boot.conf` are staged. The result is a repeatable boot path where updates look like file renames on the boot FS, while customizations stay confined to `/userdata` or an explicit overlay snapshot.

## 4. Persistent Data & Configuration

### 4.1 `/userdata` mount

- The BusyBox init script `board/fsoverlay/etc/init.d/S11share` mounts `/userdata` according to `sharedevice` in `/boot/system-boot.conf`. It can use the internal partition (`INTERNAL`), tmpfs (`RAM`), the first external drive (`ANYEXTERNAL`), network/NAS shares (`NETWORK`), or specific UUIDs (`DEV` / `DEVICES`). All mount logic delegates to `system-mount` (`package/system/reglinux-scripts/scripts/system-mount`), which knows about ext, ntfs3, btrfs, exfat, NTFS health checks, and rw verification.
- `system-part` (same directory) discovers `/boot`, `/userdata`, and their parent disks to support redeployment scripts and the updater.

### 4.2 Data initialization

- `S12populateshare` (`board/fsoverlay/etc/init.d/S12populateshare`) compares `/usr/share/reglinux/datainit.list` with the actual `/userdata` tree. Missing files (ROM metadata, BIOS readmes, themes, configs) are extracted from `datainit.squashfs`, and `system.version` is copied to `/userdata/system/data.version` to avoid redundant work.
- The script also ensures persistent `udev/rules.d`, generates a `machine-id`, loads `/userdata/system/system.conf` into memory, and calls `postshare.sh` hooks.

### 4.3 Runtime configuration stores

- `/boot/system-boot.conf` – read by init scripts before `/userdata` is reachable; it controls share selection, autoresize/new UUID, GPU driver overrides, and prime settings.
- `/userdata/system/system.conf` – the primary configuration file for services, display/audio defaults, network credentials, and controller switches (`package/system/reglinux-system/system.conf`).
- `/etc/profile.d/xdg.sh` (installed by `package/system/reglinux-system`) pushes `XDG_*` paths into `/userdata` and advertises the user-customizable SDL controller DB.

## 5. Runtime Services & Init

### 5.1 Init system

- REG Linux relies on BusyBox SysV init (`BR2_INIT_SYSV`). `board/fsoverlay` provides the system-wide `/etc/init.d/S*` scripts:
  - The early helper shipped with `reglinux-msg` starts the custom IPC daemon so other boot scripts can issue commands through it.
  - `S08connman` configures ConnMan, and optionally toggles Wi-Fi radios.
  - `S11share` and `S12populateshare` mount `/userdata` and seed it before higher-level daemons start.
  - `S18governor`, `S26system`, `S27brightness`, `S31sixad`, etc. apply CPU governors, keyboard layouts, brightness, PS3 pad modes, and timezone settings.
  - `S61cec` emits HDMI-CEC standby commands when requested, and `S99userservices` starts user-defined scripts located in `/userdata/system/services`.

### 5.2 Service selection

- `system.services` (in `system.conf`) enumerates optional daemons such as SAMBA, SSH, LOGS, Syncthing, etc. The helper `system-services` modifies that list, and `S99userservices` cross-references the string with `usr/share/reglinux/services` and `/userdata/system/services`. Each executable receives `start`/`stop` arguments and adheres to BusyBox init conventions.

## 6. Graphics, Audio, and Input Stack

- SDL2 and SDL3 are always built (`BR2_PACKAGE_REGLINUX_SDL2`, `BR2_PACKAGE_REGLINUX_SDL3`).
- Graphics targets are grouped in `Config.in.targets` into GLES2/GLES3 families. Those symbols select Mesa variants (Panfrost/Panthor, Vulkan drivers, IMG blobs) and fine-tune windowing stacks.
- Wayland (`seatd`, `wayland-protocols`, `reglinux-sway`, `reglinux-xwayland`) is enabled for modern GPUs; older boards stay on SDL/Xorg. Board overlays in `board/<vendor>/<soc>/fsoverlay` carry backend-specific configs.
- Audio is handled by Batocera’s ALSA helpers (`package/batocera/core/batocera-audio`) plus `S27audioconfig`. Default volume, device selection, and profiles are persisted in `system.conf`.
- Controllers rely on the expanded HID kernel fragment plus userspace helpers (e.g., `xarcade2jstick`, `mk_arcade_joystick_rpi`). `/etc/init.d/S31sixad` toggles PS3 support depending on `controllers.*` keys.

## 7. Gaming & Application Stack

- **Front-end** – EmulationStation (REG build) lives under `package/emulationstation/reglinux-emulationstation`. Runtime scripts (`S31emulationstation`, `emulationstation-standalone`) pick displays, set rotations, and launch Sway or X11 sessions.
- **Emulators** – Standalone engines reside in `package/emulators/` (e.g., DuckStation, PCSX2, PPSSPP, Ryujinx, Vita3K, RPCS3, Yuzu replacements). Buildroot `.mk` files copy BIOS stubs, shaders, or configs into `datainit`.
- **RetroArch & libretro** – `package/retroarch/` contains RetroArch itself, assets, joypad autoconfigs, shaders, and per-core Buildroot packages under `package/emulators/libretro/`.
- **Engines & Ports** – Native ports (OpenJazz, Cannonball, TheForceEngine) live in `package/ports/`, often installing default config to `/usr/share/reglinux/datainit/system/configs`.
- **System helpers** – `package/system/reglinux-configgen` (Python + ZeroMQ) generates emulator configuration per game, reading from `/usr/share/reglinux/datainit/system`.

## 8. Networking & External Storage

- **Storage backends** – `S11share` and `system-mount` allow mixing internal/external drives, NAS shares (NFS/CIFS), and per-directory mounts. Subdirectories can be exported individually (ROMS, SAVES, BIOS, etc.).
- **Transport services** – Samba/KSmbd (`package/system/reglinux-samba`), NFS (`custom/package/nfs-utils`), SSH/Dropbear (`custom/package/dropbear`), wsdd discovery, and Syncthing.
- **USB & MTP** – USB mass storage and `umtp-responder` are enabled globally so `/userdata` can appear as a drive on host PCs.
- **Wi-Fi & Bluetooth** – ConnMan + IWD + BlueZ stack.

## 9. Updates, Recovery, and Overlay Control

- `system-upgrade` (`package/system/reglinux-scripts/scripts/system-upgrade`) downloads `boot-<board>.tar.zst` from GitHub or a dev URL, verifies optional `.md5`, remounts `/boot` read/write, and untars the payload under `/boot`.  
- The initramfs sees the `.update` suffix, replaces the active SquashFS/firmware/modules, and drops `REG_UPDATE`. On the next boot, the rescue rootfs from `/boot/rescue` mounts as the lowerdir so it can finish migrations (resize `/userdata`, regenerate caches, etc.) before switching back.
- `system-save-overlay` allows advanced users to persist manual `/` tweaks by writing an ext4 file (`/boot/boot/overlay`) and syncing the RAM overlay into it.
- `system-rescue` (part of `reglinux-rescue`) gives a minimal environment for flashing, updating, or checking disks. The rescue image is downloaded per architecture in `package/system/reglinux-rescue`.

## 10. Package Catalog Highlights

`package/` is organized by functional domains:

- `system/` – base OS features: reglinux-system (versioning, datainit, configs), reglinux-scripts (CLI utilities), reglinux-bezels, reglinux-msg, reglinux-zramswap, reglinux-samba, reglinux-rescue, etc.
- `gpu/` – Mesa forks, vendor-specific binaries (IMG PowerVR), and Vulkan layers.
- `emulators/`, `retroarch/`, `ports/`, `games/` – primary application stack.
- `batocera/` – upstream helpers still shared with Batocera (audio, triggerhappy, case utils) while migrating branding.
- `controllers/`, `cases/`, `utils/` – hardware addons, fan controllers, sensors, log helpers.
- `network/`, `toolchain/`, `firmwares/` – connectivity daemons, optional Bootlin toolchains, and firmware bundles.

Each Buildroot package installs configs into `/usr/share/reglinux/datainit` so that `/userdata` is populated deterministically on first boot.

## 11. Board Support Architecture

- Vendors live under `board/<vendor>/`. Each SoC/board folder typically includes:
  - `fsoverlay/` – files copied into `/` for that board only (extra init scripts, device-specific firmware).
  - `patches/` – kernel/U-Boot/device tree fixes.
  - `create-boot-script.sh` – invoked by the post-image hook to copy binaries into the staging boot partition and adjust configuration (extlinux, cmdline, EFI, etc.).
  - `genimage.cfg` – disk layout describing bootloader gaps, partition sizes, and special blobs.
  - Additional helper scripts (`build-uboot.sh`, device calibration tools, panel configs).
- `board/fsoverlay/` contains global init scripts and configs for all targets.
- `board/reglinux/` hosts shared kernel fragments, patches, and packaging scripts for modules/firmware.

## 12. Developer Entry Points

- **Add a board** – copy an existing `.board` file under `configs/`, tweak the toolchain/kernel/overlay directives, and author a matching `board/<vendor>/<soc>/<board>/` directory with boot + genimage scripts.
- **Tune the base system** – edit `package/system/reglinux-system/*` for configuration defaults, datainit content, or version numbering (`reglinux-system.mk`).
- **Extend runtime services** – drop new scripts in `/usr/share/reglinux/services` via a package.
- **Build & test** – run `make <board>-build` to produce SD images under `output/<board>/images/<variant>/`. Boot them, inspect `/userdata/system/logs/`, and use `system-upgrade manual` to test OTA flows without reflashing.

By separating immutable system images, a writable userdata volume, and message-driven runtime configuration, REG Linux remains portable across boards while still allowing users and developers to customize behavior safely.
