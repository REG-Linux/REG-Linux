# emulators/libretro

**Libretro cores for RetroArch**

This directory contains libretro emulator cores built as standalone packages. Each subdirectory produces a single `.so` core installed under `/usr/lib/libretro/`.

## Build System

All cores share the standard libretro build helpers:

- **generic-package**: For Makefile-based cores (most common)
- **cmake-package**: For CMake-based cores (ppsspp, mgba, flycast)

Per-platform `LIBRETRO_PLATFORM` values and architecture-specific flags are set individually in each package's `.mk` file.

## Installation

All cores are installed to:

```
/usr/lib/libretro/<core>_libretro.so
```

RetroArch automatically scans this directory for available cores.

## Available Cores

### Console Cores

| Core                        | System                          | Build System | Dependencies             |
| --------------------------- | ------------------------------- | ------------ | ------------------------ |
| `libretro-gpsp`             | Game Boy Advance                | generic      | -                        |
| `libretro-mgba`             | Game Boy Advance                | cmake        | libzip, libpng, zlib     |
| `libretro-gambatte`         | Game Boy/Game Boy Color         | generic      | -                        |
| `libretro-nestopia`         | NES                             | generic      | -                        |
| `libretro-fceumm`           | NES                             | generic      | -                        |
| `libretro-snes9x`           | SNES                            | generic      | zlib                     |
| `libretro-bsnes`            | SNES                            | generic      | -                        |
| `libretro-bsnes-jg`         | SNES                            | generic      | -                        |
| `libretro-genesisplusgx`    | Sega Genesis/Mega Drive         | generic      | -                        |
| `libretro-pcsx`             | PlayStation                     | generic      | -                        |
| `libretro-ppsspp`           | PSP                             | cmake        | libgl/libgles            |
| `libretro-mupen64plus-next` | Nintendo 64                     | generic      | libgl/libgles, host-nasm |
| `libretro-parallel-n64`     | Nintendo 64                     | generic      | -                        |
| `libretro-flycast`          | Dreamcast/Naomi                 | cmake        | libgl/libgles            |
| `libretro-kronos`           | Sega Saturn                     | generic      | libgl/libgles            |
| `libretro-beetle-saturn`    | Sega Saturn                     | generic      | -                        |
| `libretro-beetle-psx`       | PlayStation                     | generic      | -                        |
| `libretro-beetle-pce`       | TurboGrafx-16/PC Engine         | generic      | -                        |
| `libretro-beetle-pce-fast`  | TurboGrafx-16/PC Engine (fast)  | generic      | -                        |
| `libretro-beetle-pcfx`      | PC-FX                           | generic      | -                        |
| `libretro-vba-m`            | Game Boy Advance                | generic      | -                        |
| `libretro-sameboy`          | Game Boy/Game Boy Color         | generic      | -                        |
| `libretro-gearboy`          | Game Boy/Game Boy Color         | generic      | -                        |
| `libretro-stella`           | Atari 2600                      | generic      | -                        |
| `libretro-a5200`            | Atari 5200                      | generic      | -                        |
| `libretro-atari800`         | Atari 8-bit                     | generic      | -                        |
| `libretro-bluemsx`          | MSX                             | generic      | -                        |
| `libretro-fbneo`            | Arcade (CPS1/2/3, NeoGeo, etc.) | generic      | -                        |
| `libretro-fbalpha`          | Arcade (older)                  | generic      | -                        |
| `libretro-mame`             | Arcade (MAME)                   | generic      | alsa-lib                 |
| `libretro-mame2003-plus`    | Arcade (MAME 0.78)              | generic      | -                        |
| `libretro-mame2010`         | Arcade (MAME 0.139)             | generic      | -                        |
| `libretro-imame`            | Arcade (Irem)                   | generic      | -                        |
| `libretro-neocd`            | Neo Geo CD                      | generic      | -                        |
| `libretro-opera`            | 3DO                             | generic      | -                        |
| `libretro-panda3ds`         | Nintendo 3DS                    | generic      | -                        |
| `libretro-melonds-ds`       | Nintendo DS                     | generic      | -                        |
| `libretro-puae`             | Amiga                           | generic      | -                        |
| `libretro-puae2021`         | Amiga                           | generic      | -                        |
| `libretro-vice`             | Commodore 64/128/etc.           | generic      | -                        |
| `libretro-hatari`           | Atari ST                        | generic      | -                        |
| `libretro-cap32`            | Amstrad CPC                     | generic      | -                        |
| `libretro-crackshot`        | MSX                             | generic      | -                        |
| `libretro-xmil`             | Sharp X68000                    | generic      | -                        |
| `libretro-pc88`             | NEC PC-8801                     | generic      | -                        |
| `libretro-emuscv`           | SNK Neo Geo Pocket              | generic      | -                        |
| `libretro-geargrafx`        | NEC TurboGrafx-16               | generic      | -                        |
| `libretro-gearlynx`         | Atari Lynx                      | generic      | -                        |
| `libretro-gearcoleco`       | ColecoVision                    | generic      | -                        |
| `libretro-gearsystem`       | Sega Master System/Game Gear    | generic      | -                        |
| `libretro-clownmdemu`       | Sega Genesis/Mega Drive         | generic      | -                        |
| `libretro-picodrive`        | Sega Genesis/Mega Drive         | generic      | -                        |
| `libretro-blastem`          | Sega Genesis/Mega Drive         | generic      | -                        |
| `libretro-geolith`          | Sega Genesis/Mega Drive         | generic      | -                        |
| `libretro-watara`           | Watara Supervision              | generic      | -                        |
| `libretro-vecx`             | Vectrex                         | generic      | -                        |
| `libretro-81`               | ZX81                            | generic      | -                        |
| `libretro-minivmac`         | Macintosh                       | generic      | -                        |
| `libretro-same-cdi`         | Philips CD-i                    | generic      | -                        |
| `libretro-play`             | PlayStation 2                   | generic      | -                        |
| `libretro-azahar`           | Nintendo 3DS                    | generic      | -                        |
| `libretro-holani`           | Atari 2600                      | generic      | -                        |
| `libretro-applewin`         | Apple II                        | generic      | -                        |
| `libretro-dosbox-pure`      | DOS                             | generic      | -                        |

### Architecture Support

| Architecture        | Cores Supported | Notes                                     |
| ------------------- | --------------- | ----------------------------------------- |
| **x86_64**          | All             | Full support with dynamic recompilation   |
| **aarch64 (ARM64)** | Most            | Some cores use ARM-specific optimizations |
| **armv7 (ARM32)**   | Most            | Limited dynarec support                   |
| **riscv64**         | Limited         | Only software rendering cores             |

### Graphics Backend Support

| Backend           | Cores                             | Notes                                            |
| ----------------- | --------------------------------- | ------------------------------------------------ |
| **OpenGL**        | Most 3D cores                     | Desktop OpenGL (x86_64)                          |
| **OpenGL ES 3.x** | Most 3D cores                     | ARM devices with GLES3                           |
| **OpenGL ES 2.x** | Most 3D cores                     | Older ARM devices with GLES2                     |
| **Vulkan**        | flycast, ppsspp, mupen64plus-next | Optional, requires `BR2_PACKAGE_REGLINUX_VULKAN` |
| **Software**      | All 2D cores                      | No GPU required                                  |

## Dependencies

### Common Dependencies

| Dependency              | Used By           | Purpose                          |
| ----------------------- | ----------------- | -------------------------------- |
| `BR2_INSTALL_LIBSTDCPP` | All cores         | C++ standard library             |
| `BR2_GCC_ENABLE_OPENMP` | Some cores        | OpenMP parallelism (bsnes, mame) |
| `libgl`                 | 3D cores (x86_64) | Desktop OpenGL rendering         |
| `libgles`               | 3D cores (ARM)    | OpenGL ES rendering              |
| `zlib`                  | snes9x, mgba      | Compression                      |
| `libpng`                | mgba              | PNG image support                |
| `libzip`                | mgba              | ZIP archive support              |
| `alsa-lib`              | mame              | Audio output (optional)          |
| `ffmpeg`                | ppsspp (optional) | Video decoding                   |
| `host-nasm`             | mupen64plus-next  | x86 assembly                     |

### Optional Dependencies

| Dependency                    | Used By            | Purpose            |
| ----------------------------- | ------------------ | ------------------ |
| `BR2_PACKAGE_REGLINUX_VULKAN` | flycast, ppsspp    | Vulkan rendering   |
| `BR2_PACKAGE_PULSEAUDIO`      | mame               | PulseAudio support |
| `BR2_PACKAGE_FFMPEG`          | ppsspp (musl/mips) | System ffmpeg      |

## Platform-Specific Optimizations

### Raspberry Pi

| Target    | Platform Value   | Cores Optimized                     |
| --------- | ---------------- | ----------------------------------- |
| `BCM2835` | `rpi1`           | gpsp, stella, snes9x, pcsx, vice    |
| `BCM2836` | `rpi2`           | stella, snes9x, pcsx, vice          |
| `BCM2837` | `rpi3_64`        | stella, fbneo, pcsx, vice           |
| `BCM2711` | `rpi4`/`rpi4_64` | stella, snes9x, pcsx, flycast, vice |
| `BCM2712` | `rpi5`/`rpi5_64` | stella, snes9x, pcsx, flycast, vice |

### Rockchip

| Target   | Platform Value | Cores Optimized |
| -------- | -------------- | --------------- |
| `RK3326` | `rk3326`       | pcsx, fbneo     |
| `RK3399` | `rockpro64`    | kronos          |
| `RK3568` | `rk3568`       | flycast         |

### Amlogic

| Target     | Platform Value                 | Cores Optimized               |
| ---------- | ------------------------------ | ----------------------------- |
| `S922X`    | `CortexA73_G12B`/`odroid-n2`   | snes9x, pcsx, flycast, kronos |
| `S905`     | `armv cortexa9 neon hardfloat` | pcsx                          |
| `S905GEN3` | `odroid-c4`                    | kronos                        |

### Other Platforms

| Target         | Platform Value | Cores Optimized |
| -------------- | -------------- | --------------- |
| `H3`           | `rpi2`         | pcsx            |
| `H5`           | `h5`           | pcsx            |
| `RK3128`       | `rpi2`         | pcsx            |
| `JZ4770`       | `jz4770`       | gpsp            |
| `XU4`          | `odroid`/`XU4` | kronos, flycast |
| `LIBRETECH_H5` | `h5`           | pcsx            |

## Build Configuration

### Enabling Cores

Cores can be enabled in `menuconfig`:

```
Emulators  --->
    libretro cores  --->
        <*> libretro-gpsp
        <*> libretro-mgba
        <*> libretro-snes9x
        <*> libretro-pcsx
```

### Disabling Cores

To save build time and space, disable unused cores:

```
Emulators  --->
    libretro cores  --->
        [ ] libretro-play
        [ ] libretro-mame
        [ ] libretro-vice
```

## Known Issues

### Build Issues

1. **mame**: Very large build, requires significant RAM. Limited to 32 parallel jobs.
2. **ppsspp**: MIPS and musl builds require system ffmpeg.
3. **mupen64plus-next**: Requires host-nasm for x86_64 builds.

### Runtime Issues

1. **flycast**: Vulkan may be slower than OpenGL on some drivers.
2. **mame**: Requires BIOS and ROM files in correct format.
3. **ppsspp**: Some games require specific compatibility settings.
4. **vice**: Multiple cores built (x64, x128, xpet, etc.), select appropriate core per system.

## BIOS Files

Many cores require BIOS files for accurate emulation:

| Core               | BIOS File                                      | Path                                | Required                          |
| ------------------ | ---------------------------------------------- | ----------------------------------- | --------------------------------- |
| `libretro-gpsp`    | `gba_bios.bin`                                 | `/usr/share/reglinux/bios/`         | Optional (improves compatibility) |
| `libretro-mgba`    | `gba_bios.bin`                                 | `/usr/share/reglinux/bios/`         | Optional                          |
| `libretro-pcsx`    | `scph5500.bin`, `scph5501.bin`, `scph5502.bin` | `/usr/share/reglinux/bios/`         | Optional                          |
| `libretro-flycast` | `dc_boot.bin`, `dc_flash.bin`                  | `/usr/share/reglinux/bios/flycast/` | Required                          |
| `libretro-kronos`  | `saturn_bios.bin`                              | `/usr/share/reglinux/bios/`         | Optional                          |
| `libretro-mame`    | Various                                        | `/usr/share/lr-mame/hash/`          | Required for some games           |

## References

- **Libretro Documentation**: https://docs.libretro.com/
- **RetroArch**: https://www.retroarch.com/
- **Libretro Cores**: https://www.libretro.com/
- **Buildroot External Tree**: https://buildroot.org/
