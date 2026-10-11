# ymir

Sega Saturn emulator. Upstream: https://github.com/StrikerX3/Ymir

## Package Overview

Ymir is a work-in-progress Sega Saturn emulator that requires clang and EGL. It uses SDL3 for its frontend and has been patched to work with system libraries instead of bundled dependencies.

**Current Version:** v0.2.1 (released January 10, 2026)

## Dependencies

### Runtime Dependencies

- `clang` - Required for compilation (C++20 support)
- `libegl` - OpenGL ES support
- `sdl3` - SDL3 frontend
- `wayland` & `wayland-protocols` - Wayland display server support
- `libxkbcommon` - Keyboard handling

### Library Dependencies

- `cereal` - Serialization library
- `cxxopts` - Command-line option parsing
- `date` - Date/time utilities
- `fmt` - Formatting library
- `json-for-modern-cpp` (nlohmann-json) - JSON parsing
- `libcurl` - HTTP/HTTPS support (dynamic linking)
- `nghttp3` - HTTP/3 support
- `rtmidi` - MIDI support
- `semver` - Semantic versioning
- `stb` - Single-file public domain libraries
- `tomlplusplus` - TOML parsing

## Patches

The package includes 4 patches to adapt Ymir for Buildroot cross-compilation:

1. **001-use-system-sdl3.patch** - Forces CMake to use system SDL3 instead of bundled version
2. **002-no-stb-cmake.patch** - Removes stb find_package requirement (uses system stb headers)
3. **003-libcurl-dynamic-cynamic-cmake.patch** - Links against dynamic libcurl instead of static
4. **004-about-window-no-ngtcp2.patch** - Removes ngtcp2 dependency from About dialog (HTTP/3 not available in this build)

## Build Configuration

### Build System

- **Backend**: Ninja (faster builds)
- **Compiler**: Clang via Buildroot toolchain wrapper (`clang.br_real`, `clang++.br_real`)
- **C++ Standard**: C++20 required

### CMake Options

```cmake
-DYmir_DEV_BUILD=OFF
-DYmir_ENABLE_DEVLOG=OFF
-DYmir_ENABLE_UPDATE_CHECKS=OFF   # Disabled for embedded/immutable systems
-DYmir_EXTRA_INLINING=ON
-DYmir_ENABLE_TESTS=OFF
-DYmir_ENABLE_SANDBOX=OFF
-DYmir_ENABLE_YMDASM=OFF
-DYmir_ENABLE_IMGUI_DEMO=OFF
-DYmir_AVX2=ON                      # Enabled for x86_64_v3 builds only
```

### IPO/LTO Configuration

IPO (Inter-Procedural Optimization) is conditionally enabled based on architecture:

| Architecture | IPO/LTO | Linker | Performance Gain |
| ------------ | ------- | ------ | ---------------- |
| x86_64       | ON      | lld    | 10-20%           |
| ARM64        | OFF     | bfd    | -                |
| RISC-V       | OFF     | bfd    | -                |

**Rationale:**

- x86_64 toolchains have mature clang+lld support
- ARM64/RISC-V toolchains vary in LTO compatibility
- IPO requires lld linker for proper LLVM bitcode handling
- Uses `CMAKE_LINKER` to directly invoke `ld.lld` (avoids `-fuse-ld` wrapper issues)

### Known Issues

1. **IPO/LTO on ARM/RISC-V**: Disabled due to toolchain variability; may be enabled in future releases
2. **ngtcp2 Missing**: HTTP/3 support is patched out; only HTTP/2 via nghttp2 is available
3. **Architecture Support**: Requires ARM64 or x86-64 (AArch64/x86_64_v3 recommended)
4. **BIOS Required**: Needs Sega Saturn IPL ROM in `roms/ipl` directory for operation

## Installation

The emulator binary is installed to `/usr/bin/ymir` on the target system.

## Configuration

First-run creates configuration directories alongside the executable. Place BIOS files in:

- `roms/ipl/` - Saturn IPL BIOS (required)
- `roms/cdb/` - CD block ROM (for low-level CD emulation)

## Supported Formats

- MAME CHD
- BIN+CUE
- IMG+CCD
- MDF+MDS
- ISO

## Performance Notes

- AVX2 optimization is automatically enabled for x86_64_v3 builds
- Requires EGL-capable GPU driver
- Wayland is the primary display backend

## See Also

- [Upstream Repository](https://github.com/StrikerX3/Ymir)
- [Sega Saturn Emulation](https://wiki.reglinux.org/segasaturn)
