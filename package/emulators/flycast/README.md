# flycast

**Sega Dreamcast, Naomi, and Atomiswave emulator**

Upstream: https://github.com/flyinghead/flycast

## Version

- **Version**: `v2.6`
- **License**: GPLv2

## Architecture Support

| Architecture          | Graphics Backend    | Notes                                |
| --------------------- | ------------------- | ------------------------------------ |
| **x86_64**            | OpenGL (Desktop GL) | Default                              |
| **ARM (GLES3)**       | OpenGL ES 3.x       | Auto-detected                        |
| **ARM (GLES2)**       | OpenGL ES 2.x       | Fallback                             |
| **Any (with Vulkan)** | Vulkan              | When `BR2_PACKAGE_REGLINUX_VULKAN=y` |

## Dependencies

### Required Runtime Dependencies

| Package    | Purpose                                     | CMake Option                  |
| ---------- | ------------------------------------------- | ----------------------------- |
| `sdl2`     | Input, audio, windowing, OpenGL context     | `-DUSE_HOST_SDL=ON`           |
| `libzip`   | Archive handling (ZIP, 7z)                  | `-DUSE_HOST_LIBZIP=ON`        |
| `libcurl`  | Network features (firmware downloads, etc.) | `find_package(CURL REQUIRED)` |
| `alsa-lib` | Audio output on Linux                       | `-DUSE_ALSA=ON`               |

### Optional Runtime Dependencies

| Package        | Purpose                     | CMake Option             | Default       |
| -------------- | --------------------------- | ------------------------ | ------------- |
| `libpulse`     | PulseAudio support          | `-DUSE_PULSEAUDIO=ON`    | ON            |
| `libao`        | Audio output abstraction    | (auto-detected)          | ON            |
| `libminiupnpc` | UPnP networking for netplay | (auto-detected)          | ON            |
| `glslang`      | Vulkan shader compilation   | `-DUSE_HOST_GLSLANG=OFF` | OFF (bundled) |
| `libcdio`      | CD-ROM access               | `-DUSE_LIBCDIO=ON`       | OFF           |
| `libjuice`     | WebRTC for netplay          | (bundled)                | ON            |
| `libevdev`     | Linux input (if no SDL2)    | (auto-detected)          | Auto          |
| `libudev`      | Device hotplug              | (auto-detected)          | Auto          |

### Build Dependencies

| Package          | Purpose                                |
| ---------------- | -------------------------------------- |
| `cmake`          | Build system generator                 |
| `ninja`          | Build backend                          |
| `git`            | Source retrieval (with submodules)     |
| `python`         | Build scripts                          |
| `vulkan-headers` | Vulkan API headers (if Vulkan enabled) |

### Removed Dependencies (Not Required)

| Package    | Reason                                                             |
| ---------- | ------------------------------------------------------------------ |
| `elfutils` | **libelf is bundled** in `core/deps/libelf/`                       |
| `libpng`   | Not directly used by flycast                                       |
| `boost`    | Only used for profiler (`ENABLE_FC_PROFILER`), disabled by default |

## Build Configuration

### CMake Options

```cmake
# Core options
-DCMAKE_BUILD_TYPE=Release
-DBUILD_SHARED_LIBS=OFF
-DLIBRETRO=OFF
-DUSE_HOST_SDL=ON

# Audio
-DUSE_ALSA=ON              # ALSA audio (default: ON)
-DUSE_PULSEAUDIO=ON        # PulseAudio (default: ON)

# Archives
-DUSE_HOST_LIBZIP=ON       # Use system libzip (default: ON)

# Graphics
-DUSE_OPENGL=ON            # Desktop OpenGL (x86_64)
-DUSE_GLES=ON              # OpenGL ES (ARM)
-DUSE_GLES2=OFF            # OpenGL ES 2 (fallback)
-DUSE_VULKAN=ON/OFF        # Vulkan (optional)
-DUSE_HOST_GLSLANG=OFF     # Use bundled glslang (default: OFF)

# Optional features (disabled)
-DUSE_LIBCDIO=OFF          # CD-ROM access
-DUSE_LUA=OFF              # Lua scripting
-DENABLE_FC_PROFILER=OFF   # Profiler support (requires boost)
-DUSE_DISCORD=OFF          # Discord Rich Presence
-DUSE_BREAKPAD=OFF         # Crash reporting (disabled on musl)
```

### Platform-Specific Optimizations

| Target        | CMake Option     | Compiler Flags                                  |
| ------------- | ---------------- | ----------------------------------------------- |
| **RK3399**    | `-DRK3399=ON`    | `-mcpu=cortex-a72 -mtune=cortex-a72.cortex-a53` |
| **RK3568**    | `-DRK3568=ON`    | `-mcpu=cortex-a55 -mtune=cortex-a55`            |
| **RPi4**      | `-DRPI4=ON`      | `-mcpu=cortex-a72 -mtune=cortex-a72`            |
| **RPi5**      | `-DRPI5=ON`      | `-mcpu=cortex-a76 -mtune=cortex-a76`            |
| **OdroidXU4** | `-DODROIDXU4=ON` | `-mcpu=cortex-a15 -mtune=cortex-a15.cortex-a7`  |
| **S922X**     | `-DS922X=ON`     | `-mcpu=cortex-a73 -mtune=cortex-a73.cortex-a53` |

## Patches

### `000-makefile-additions.patch`

Adds platform-specific optimization flags to the upstream CMakeLists.txt:

- **New CMake options**: `RK3399`, `RK3568`, `RPI4`, `RPI5`, `ODROIDXU4`, `S922X`, `USE_MALI`
- **Optimization flags**: `-O3 -mcpu=<cpu> -mtune=<cpu>` for each platform
- **Mali support**: `-DUSE_MALI=ON` links against Mali GPU libraries

This patch is essential for embedded platforms to get optimal performance.

## Graphics Backend Selection

The graphics backend is automatically chosen based on the target architecture:

```makefile
# x86_64: Desktop OpenGL
ifeq ($(BR2_PACKAGE_SYSTEM_TARGET_X86_64_ANY),y)
    FLYCAST_CONF_OPTS += -DUSE_OPENGL=ON

# GLES3 platforms: OpenGL ES 3.x
else ifeq ($(BR2_PACKAGE_HAS_GLES3),y)
    FLYCAST_CONF_OPTS += -DUSE_GLES=ON -DUSE_GLES2=OFF -DUSE_OPENGL=ON

# GLES2 platforms: OpenGL ES 2.x (fallback)
else ifeq ($(BR2_PACKAGE_HAS_GLES2),y)
    FLYCAST_CONF_OPTS += -DUSE_GLES2=ON -DUSE_GLES=OFF -DUSE_OPENGL=ON
endif

# Vulkan: Optional, enabled via BR2_PACKAGE_REGLINUX_VULKAN
ifeq ($(BR2_PACKAGE_REGLINUX_VULKAN),y)
    FLYCAST_CONF_OPTS += -DUSE_VULKAN=ON
else
    FLYCAST_CONF_OPTS += -DUSE_VULKAN=OFF
endif
```

## Installation Paths

| Path                  | Content                           |
| --------------------- | --------------------------------- |
| `/usr/bin/flycast`    | Main executable                   |
| `/usr/share/flycast/` | Data files (firmware, BIOS, etc.) |
| `~/.flycast/`         | User configuration, saves, states |

## Configuration

### BIOS/Firmware

Flycast requires the following BIOS files in `~/.flycast/`:

| File           | Description            | Required             |
| -------------- | ---------------------- | -------------------- |
| `dc_boot.bin`  | Dreamcast BIOS         | ✅ Yes               |
| `dc_flash.bin` | Dreamcast flash memory | ✅ Yes               |
| `naomi.bin`    | Naomi BIOS             | For Naomi games      |
| `awbios.zip`   | Atomiswave BIOS        | For Atomiswave games |

### Video Settings

Config file: `~/.flycast/emulator.cfg`

```ini
[pvr]
Renderer = OpenGL       # Options: OpenGL, GLES, Vulkan
FullScreen = yes
Width = 1920
Height = 1080
VSync = yes
```

### Audio Settings

```ini
[audio]
backend = alsa          # Options: alsa, pulse, ao
Volume = 100
```

## Technical Details

### Emulated Hardware

| System             | Status       | Notes               |
| ------------------ | ------------ | ------------------- |
| **Sega Dreamcast** | ✅ Excellent | Primary target      |
| **Naomi**          | ✅ Excellent | Arcade counterpart  |
| **Naomi 2**        | ⚠️ Good      | More demanding      |
| **Atomiswave**     | ✅ Excellent | Sammy arcade system |
| **Sega Hikaru**    | ⚠️ Good      | Similar to Naomi    |

### Key Components

| Component   | Implementation                           |
| ----------- | ---------------------------------------- |
| **CPU**     | SH-4 dynarec (x86_64, ARM64, ARMv7)      |
| **GPU**     | PowerVR 2 emulation (OpenGL/GLES/Vulkan) |
| **Audio**   | ARM7 AICA emulation (ALSA/PulseAudio)    |
| **Input**   | SDL2 gamepad/keyboard                    |
| **Netplay** | libjuice (WebRTC-based)                  |

### Memory Management

- **Main RAM**: 16MB (Dreamcast), 32MB (Naomi)
- **VRAM**: 8MB texture memory
- **Sound RAM**: 2MB AICA RAM
- Uses JIT compilation for SH-4 → x86_64/ARM translation

## Known Issues

### Build Issues

1. **miniupnpc version mismatch**: Some distributions have incompatible miniupnpc versions. If build fails, try `-DUSE_MINIUPNPC=OFF`.

2. **libjuice compilation**: May fail on older toolchains. The bundled version is usually compatible.

3. **Vulkan + glslang**: When using Vulkan, ensure glslang is available or use `-DUSE_HOST_GLSLANG=OFF` for bundled version.

### Runtime Issues

1. **Audio crackling**: Try switching ALSA backend or adjusting buffer sizes in `emulator.cfg`.

2. **Input lag**: Enable `-DUSE_EVDEV=ON` for direct evdev input (bypasses SDL2).

3. **Vulkan performance**: May be slower than OpenGL on some drivers. Test both backends.

4. **Netplay**: Requires open ports or UPnP router. libminiupnpc helps with automatic port forwarding.

## References

- **Official Website**: https://flycast.dev/
- **GitHub**: https://github.com/flyinghead/flycast
- **Wiki**: https://github.com/flyinghead/flycast/wiki
- **Discord**: https://discord.gg/8FqVpVT
- **Libretro Core**: https://github.com/libretro/flycast

## See Also

- [reicast](https://github.com/reicast/reicast-emulator) - Predecessor project
- [Redream](https://redream.io/) - Commercial Dreamcast emulator
- [MAME](https://www.mamedev.org/) - Also emulates Naomi/Atomiswave
