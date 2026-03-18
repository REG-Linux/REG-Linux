# REG Linux on MiSTer FPGA (DE10-Nano) — Hybrid Architecture Plan

## Overview

Port REG Linux to the Terasic DE10-Nano (MiSTer FPGA platform) as a **hybrid system**:
FPGA cores for cycle-accurate retro emulation + software emulators for everything else,
unified behind a Slint + Skia software-rendered UI.

## Hardware Specs

| Component       | Spec |
|-----------------|------|
| SoC             | Intel Cyclone V 5CSEBA6U23I7 |
| CPU (HPS)       | Dual Cortex-A9 @ 800MHz, ARMv7, NEON |
| RAM             | 1GB DDR3 (shared HPS + FPGA) |
| FPGA            | ~110K logic elements |
| GPU             | **None** on the HPS side — Mesa swrast (softpipe/llvmpipe) |
| Video           | FPGA drives ADV7513 HDMI transmitter directly |
| HPS Framebuffer | 8MB at physical 0x22000000 (up to 1080p, RGBA) |
| Bridges         | LW-H2F (registers @ 0xFF200000), H2F (bulk @ 0xC0000000), F2H (DMA) |

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        REG Linux on DE10-Nano                   │
│                                                                 │
│  ┌──────────────┐    ┌──────────────────┐    ┌───────────────┐  │
│  │   Slint UI   │    │  libmister-fpga  │    │   RetroArch   │  │
│  │  (Rust/Skia) │    │     (Rust)       │    │  (libretro)   │  │
│  │              │    │                  │    │               │  │
│  │ Game browser │◄──►│ Core lifecycle   │    │ SW emulation  │  │
│  │ Settings     │    │ Input forwarding │    │ GB, GBC, 2600 │  │
│  │ Scraper      │    │ ROM transfer     │    │               │  │
│  └──────┬───────┘    └────────┬─────────┘    └───────┬───────┘  │
│         │                     │                      │          │
│  ┌──────▼─────────────────────▼──────────────────────▼───────┐  │
│  │              Linux Kernel (MiSTer 5.15 fork)              │  │
│  │  KMS/DRM  │  /dev/mem  │  libinput  │  USB  │  Network   │  │
│  └──────┬────────────┬────────────┬──────────────────────────┘  │
│         │            │            │                              │
├─────────▼────────────▼────────────▼──────────────────────────────┤
│                    Cyclone V SoC Hardware                        │
│                                                                 │
│  ┌────────────┐  LW Bridge   ┌────────────────────────────────┐ │
│  │  ARM HPS   │◄────────────►│         FPGA Fabric            │ │
│  │ 2x A9      │  H2F Bridge  │                                │ │
│  │ 800MHz     │◄────────────►│  ┌──────────┐  ┌───────────┐  │ │
│  │            │  F2H Bridge  │  │ MiSTer   │  │  128MB     │  │ │
│  │ 1GB DDR3   │◄────────────►│  │ Core     │  │  SDRAM     │  │ │
│  └────────────┘              │  │ (.rbf)   │  │  Board     │  │ │
│                              │  └─────┬────┘  └───────────┘  │ │
│       HPS FB ──────────────► │        │                       │ │
│       (8MB @ 0x22000000)     │        ▼                       │ │
│                              │  ┌──────────┐                  │ │
│                              │  │ ADV7513  │──► HDMI Out      │ │
│                              │  │ HDMI TX  │                  │ │
│                              │  └──────────┘                  │ │
│                              └────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

## MiSTer Technical Reference

### FPGA Core Loading (from Main_MiSTer fpga_io.cpp)

- FPGA programmed via direct `/dev/mem` mmap at 0xFF000000 (FPGA Manager registers)
- RBF bitstream streamed with ARM assembly ldmia/stmia for max bandwidth
- After loading: `do_bridge(enable)` activates HPS-FPGA bridges via NIC-301 remap
- Core released from reset via GPIO bit 30

### HPS-FPGA Communication

Three channels:
1. **Lightweight Bridge** (0xFF200000): Register-level core configuration
2. **Heavyweight Bridge** (0xC0000000): Bulk data transfer (ROM loading, framebuffer)
3. **GPIO-SPI Protocol**: Software SPI with 3 chip-selects:
   - SSPI_FPGA_EN (1<<18): Direct core communication
   - SSPI_OSD_EN (1<<19): On-screen display data
   - SSPI_IO_EN (1<<20): User I/O commands (input, file transfer, SD emu)

### UIO Command Protocol (~40+ commands over SPI IO channel)

| Command | Code | Purpose |
|---------|------|---------|
| UIO_JOYSTICK0-5 | 0x02-0x03, 0x10-0x13 | Send digital joystick state |
| UIO_MOUSE | 0x04 | Send mouse delta + buttons |
| UIO_KEYBOARD | 0x05 | Send PS/2 scan code |
| UIO_FILE_TX | 0x53 | Begin file transfer (ROM) |
| UIO_FILE_TX_DAT | 0x54 | File transfer data |
| UIO_GET_SDSTAT | 0x16 | Poll SD card operation requests |
| UIO_SET_STATUS2 | 0x15 | Write core status/config bits |
| UIO_RTC | 0x22 | Send real-time clock data |
| UIO_ASTICK | 0x28 | Left analog stick |

### Video Architecture

- **FPGA cores generate video directly** → ADV7513 HDMI TX (I2C at 0x39)
- HPS framebuffer at 0x22000000 (8MB, up to 1080p) for Linux-side content
- Two display modes switchable: n=0 (Linux/HPS FB), n=1 (FPGA core)
- `slave_enable 1` via `/dev/MiSTer_cmd` hands display to Linux side

### Programmatic Control

- `/dev/MiSTer_cmd`: write commands like `load_core`, `force_file`, `slave_enable`
- MGL files: XML game launchers specifying core + ROM + delays
- All 300+ MiSTer cores are binary-compatible — they communicate via fixed hardware protocol

### Key Source Files (Main_MiSTer, GPL-3.0)

| File | Purpose |
|------|---------|
| fpga_io.cpp | FPGA programming, register access, SPI, bridge control |
| user_io.cpp | UIO protocol, core communication, file transfer, SD emulation |
| input.cpp | evdev input detection, translation tables, player assignment |
| video.cpp | HDMI config (ADV7513), PLL, video modes, scaler, VRR |
| spi.cpp | SPI protocol implementation, chip-select management |
| menu.cpp | Menu state machine, file browser, core selection |

### Other Projects Worth Studying

| Project | What | License |
|---------|------|---------|
| GoLEm/1FPGA | Complete MiSTer firmware rewrite in Rust | Apache-2.0 |
| mrext | Go-based web API + WebSocket for MiSTer control | GPL-3.0 |
| mr-fusion | Buildroot-based SD image builder | GPL-2.0 |
| MiSTerArch | Arch Linux ARM on MiSTer hardware | - |
| mbc | CLI tool for programmatic core/game launching | - |

## UI: Slint + Skia Software Rendering

- **LinuxKMS backend**: renders directly to DRM/KMS, no compositor needed
- `SLINT_BACKEND=linuxkms-skia-software`: CPU-only Skia, proven 60 FPS on A53 at 480x800
- On Cortex-A9 @ 800MHz: expect 15-30 FPS at 720p for static/low-animation menus
- Runtime < 300KB RAM; 1GB is comfortable
- Input via libinput (USB gamepads, keyboards)
- Cross-compilation: Skia must compile from source for armv7 (needs clang in toolchain)
- Buildroot integration documented by Slint team

---

## Phase 0 — Boot REG Linux on DE10-Nano ✅ DONE (builds successfully)

**Board target**: `reglinux-de10nano.board`
**System target**: `BR2_PACKAGE_SYSTEM_TARGET_DE10NANO`

### Board Config (`configs/reglinux-de10nano.board`)

- Toolchain: GCC 14 + musl (same as s812 Cortex-A9 board)
- CPU: `BR2_cortex_a9` + NEON + VFP + hard-float
- Kernel: MiSTer's 5.15 LTS fork via git (`MiSTer-v5.15` branch)
- Kernel headers: 5.15 (matching kernel)
- Kernel format: zImage
- Bootloader: mainline U-Boot 2025.04, `socfpga_de10_nano` defconfig
  - Output: `u-boot-with-spl.sfp` (SPL + U-Boot for Cyclone V boot ROM)
- Device tree: `socfpga_cyclone5_de10_nano` (in-tree)
- GPU: Mesa swrast (`BR2_PACKAGE_SYSTEM_SWRAST_MESA3D=y`) + llvmpipe (`BR2_PACKAGE_MESA3D_LLVM=y`)
- GL capability: GLES2 (via software rasterizer)
- No Sway compositor (no real GPU for wlroots)
- Squashfs: ZSTD compression

### GPU / Graphics Stack

The DE10-Nano has **no GPU** on the ARM HPS side. Solution:

- Created `BR2_PACKAGE_SYSTEM_SWRAST_MESA3D` in `Config.in.gpu`
  - Selects Mesa3D + Gallium swrast driver + GLES + EGL
  - Follows same pattern as LIMA, Panfrost, Freedreno configs
- Added `BR2_PACKAGE_MESA3D_LLVM=y` for llvmpipe (JIT-compiled software GL)
- DE10NANO added to GLES2 capability list in `Config.in.targets`
- SDL2/SDL3 KMSDRM backend now resolves its GL dependencies via swrast

### Bootloader

- Mainline U-Boot 2025.04 built from source via Buildroot's `BR2_TARGET_UBOOT`
- Defconfig: `socfpga_de10_nano` (upstream, well-maintained)
- Produces `u-boot-with-spl.sfp` — combined SPL + U-Boot binary
- Flashed to raw 0xA2 partition (Cyclone V SoC boot ROM convention)
- Boot script: `boot.cmd` → mkimage'd to `boot.scr`
  - Loads zImage, DTB, initrd from FAT32 boot partition
  - Console on ttyS0 @ 115200

### SD Card Image Layout (`genimage.cfg`)

```
Offset  | Partition  | Type | Content
--------|------------|------|--------
1M      | uboot      | 0xA2 | u-boot-with-spl.sfp (1M)
4M      | boot       | 0x0C | FAT32 "REGLINUX" (2G) — kernel, DTB, initrd, squashfs
after   | userdata   | 0x83 | ext4 "SHARE" (256M) — user data
```

### Kernel Config Audit

Base: MiSTer 5.15 defconfig (comprehensive HID, gamepad, WiFi, FPGA support).

Two fragment files applied on top:
1. `board/reglinux/linux-defconfig-reglinux.config` — common REG Linux fragment
2. `board/intel/de10nano/linux-defconfig-fragment.config` — DE10-Nano specific

**Already good in MiSTer base defconfig:**
- Ethernet (STMMAC/DWMAC_SOCFPGA)
- USB host (DWC2)
- FPGA manager + bridges
- I2C (Designware + GPIO)
- MMC/SD (DesignWare)
- Input (evdev, uinput, joystick, comprehensive HID)
- Filesystems (ext4, VFAT, FUSE, CONFIGFS)
- WiFi stack (cfg80211, mac80211, Realtek/Mediatek/Ralink)
- NFS + CIFS clients
- `/dev/mem` access (for FPGA programming)

**Fixed via common REG Linux fragment (overrides MiSTer defaults):**
- SquashFS + ZSTD/LZ4 (was disabled in MiSTer)
- OverlayFS (was disabled)
- ZRAM (was missing)
- USB gadget / MTP / ADB (was disabled)
- SMB server (was disabled)
- AUTOFS (was disabled)
- UINPUT, PERF_EVENTS, CPU_FREQ governors

**Fixed via DE10-Nano specific fragment:**
- IPv6 (was disabled in MiSTer defconfig, required by network services)
- ZSMALLOC (ZRAM dependency, missing from MiSTer)
- LZ4/LZO compression support (ZRAM + initrd)
- DRM (was disabled — needed for Mesa swrast + Slint KMS backend)

### Excluded Packages (too heavy for Cortex-A9 @ 800MHz or no GPU)

**Emulators excluded** (in `Config.in.emulators`):
- `FLYCAST` + `LIBRETRO_FLYCAST` — Dreamcast, too heavy
- `LIBRETRO_OPERA` — 3DO, too heavy
- `PPSSPP` + `LIBRETRO_PPSSPP` — PSP, too heavy
- `REGLINUX_MUPEN64` + `LIBRETRO_MUPEN64PLUS_NEXT` — N64, too heavy
- `VICE` + `LIBRETRO_VICE` — C64, too heavy
- `AMIBERRY_LITE` + `LIBRETRO_PUAE` — Amiga, too heavy
- `LIBRETRO_MAME2010` — old MAME, too heavy
- `DOSBOX_X` + `DOSBOX_STAGING` — DOS, too heavy
- `LIBRETRO_PC98` — PC-98, too heavy

**Ports excluded** (in `Config.in.ports`):
- `IOQUAKE3` — Quake 3, needs real GPU

**Engines excluded** (in `Config.in.engines`):
- `LIGHTSPARK` — Flash player, too heavy

**System packages excluded:**
- `SWAY` — Wayland compositor, needs GPU (removed from board config)
- `WF_RECORDER` — screen recorder, needs GPU (in `reglinux-msg/Config.in`)
- `SWITCHFIN` — video player (in `Config.in`)

### Files Created / Modified

**New files:**
- `configs/reglinux-de10nano.board` — board config
- `board/intel/de10nano/create-boot-script.sh` — boot image staging
- `board/intel/de10nano/genimage.cfg` — SD card image layout
- `board/intel/de10nano/linux-de10nano-defconfig.config` — MiSTer base kernel config
- `board/intel/de10nano/linux-defconfig-fragment.config` — DE10-Nano kernel overrides
- `board/intel/de10nano/boot/boot.cmd` — U-Boot boot script (mkimage source)
- `board/intel/de10nano/boot/boot.ini` — fallback boot config
- `board/intel/de10nano/fsoverlay/usr/bin/cputemp` — CPU temperature helper
- `board/intel/de10nano/fsoverlay/usr/bin/gputemp` — GPU temp (returns CPU temp, no GPU)
- `board/intel/de10nano/linux_patches/` — placeholder for kernel patches
- `board/intel/de10nano/patches/` — placeholder for package patches

**Modified files:**
- `package/system/reglinux-system/Config.in.targets` — DE10NANO target + GLES2 + image path
- `package/system/reglinux-system/Config.in.gpu` — added `BR2_PACKAGE_SYSTEM_SWRAST_MESA3D`
- `package/system/reglinux-system/Config.in.emulators` — DE10NANO exclusions
- `package/system/reglinux-system/Config.in.engines` — LIGHTSPARK exclusion
- `package/system/reglinux-system/Config.in.ports` — IOQUAKE3 exclusion
- `package/system/reglinux-system/Config.in` — SWITCHFIN exclusion
- `package/system/reglinux-system/reglinux-system.mk` — `REGLINUX_SYSTEM_ARCH=de10nano`
- `package/system/reglinux-msg/Config.in` — WF_RECORDER exclusion

---

## Phase 1 — Slint Frontend on HPS Framebuffer

Build a `reglinux-mister-frontend` package (Rust):
- Slint app with `backend-linuxkms` + `renderer-skia` (software mode)
- Renders to HPS framebuffer via KMS/DRM
- Game-console-style launcher: system list, ROM browser, metadata
- Input via libinput (USB gamepads)
- No theme engine — single clean built-in UI
- Add clang to host tools for Skia cross-compilation

## Phase 2 — FPGA Core Management Library

Build `libmister-fpga` Rust crate (inspired by GoLEm + Main_MiSTer):

```
libmister-fpga/
├── fpga_manager.rs    # Load .rbf via /dev/mem mmap
├── bridge.rs          # Enable/disable HPS-FPGA bridges
├── spi.rs             # GPIO-SPI protocol (3 channels)
├── uio.rs             # UIO command protocol
├── core_info.rs       # Core type detection, config string parsing
└── video.rs           # ADV7513 HDMI configuration via I2C
```

Key operations: load RBF, enable bridges, detect core, send input,
transfer files, emulate SD card.

## Phase 3 — Menu ↔ Core Video Handoff

Two video paths:
- **Menu mode**: Slint + Skia → HPS Framebuffer (0x22000000) → HDMI
- **Core running**: FPGA Core → ADV7513 HDMI TX → HDMI

Transition: user selects game → load core + ROM → switch HDMI to FPGA →
Slint suspends. User presses Home → switch back to HPS FB → Slint resumes.

## Phase 4 — Hybrid Software Emulation

| Tier | Systems | Method |
|------|---------|--------|
| FPGA | NES, SNES, Genesis, Neo Geo, GBA, etc. | MiSTer cores (.rbf) |
| Software (feasible) | GB, GBC, Atari 2600/7800, Master System | libretro + RetroArch |
| Software (stretch) | PS1, N64 | libretro (probably too slow) |

Unified UI: user doesn't know or care which path runs. Same interface,
same input config, same experience.

## Phase 5 — Polish & Community

- MiSTer core downloader/updater
- Per-core video settings (FPGA-side filter coefficients)
- Save state management
- WiFi/network config in UI
- OTA updates (existing REG Linux infra)

---

## Kernel Notes

MiSTer kernel (5.15 LTS) custom patches:
- Custom ALSA audio driver: `CONFIG_SND_MISTER_AUDIO` (SPI-based)
- CPU frequency scaling: `CONFIG_ARM_SOCFPGA_CPUFREQ`
- Extensive gamepad/controller support
- Custom framebuffer at 0x22000000 (8MB)
- FPGA manager + bridges enabled (but bypassed by userspace)
- WiFi: Realtek out-of-tree drivers

DE10-Nano device tree peripherals:
- GMAC1 (Ethernet), I2C0 (accelerometer), SPI0 (MiSTer audio), SPI1 (alt bridge)
- UART0/1, USB1 (DWC2 host), MMC0 (SD), GPIO0-2
- 3 FPGA bridges enabled, MiSTer FB node
- I2C RTCs: PCF8563, M41T81, MCP7941x (on I/O board)

Add-on boards (SDRAM, I/O) are pure FPGA-fabric — no Linux drivers needed.

## Boot / Image Layout

MiSTer production SD card layout:
- Partition 1: exFAT "MiSTer_Data" (cores, ROMs, config, linux/zImage_dtb)
- Partition 2: 0xA2 raw (U-Boot)

REG Linux layout:
- Partition 1 (offset 1M): 0xA2 raw — U-Boot SPL + U-Boot (1M)
- Partition 2 (offset 4M): FAT32 "REGLINUX" — kernel, DTB, initrd, squashfs (2G)
- Partition 3: ext4 "SHARE" — userdata (256M, expands on first boot)
