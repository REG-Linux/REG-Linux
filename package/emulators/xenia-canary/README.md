# xenia-canary

**Xbox 360 emulator**

Upstream: https://github.com/xenia-canary/xenia-canary

## Version

- **Commit**: `8bfa15ca9` (Latest, canary_experimental branch)
- **Branch**: canary_experimental

## Architecture

- **Supported**: x86_64 only
- **Not supported**: ARM, AArch64, RISC-V (emulator requires x86_64 for JIT compilation)

## Dependencies

### Runtime Dependencies

| Package          | Purpose                                                | Required? |
| ---------------- | ------------------------------------------------------ | --------- |
| `libgtk3`        | UI framework (window creation, Dear ImGui integration) | ✅ Yes    |
| `sdl2`           | Input handling, audio, window management               | ✅ Yes    |
| `vulkan-headers` | Vulkan API headers for GPU backend                     | ✅ Yes    |
| `libvulkan`      | Vulkan runtime library                                 | ✅ Yes    |
| `libx11`         | X11 window system                                      | ✅ Yes    |
| `libxcb`         | XCB protocol library                                   | ✅ Yes    |
| `alsa-lib`       | Audio output (Linux sound system)                      | ✅ Yes    |
| `liblz4`         | Compression library                                    | ✅ Yes    |
| `llvm`           | LLVM framework for shader compilation                  | ✅ Yes    |
| `clang`          | C/C++ compiler for runtime shader compilation          | ✅ Yes    |

### Build Dependencies (host tools)

| Package        | Purpose                             |
| -------------- | ----------------------------------- |
| `python-toml`  | Python TOML parsing (build scripts) |
| `host-sdl2`    | SDL2 for host build tools           |
| `cmake`        | Build system generator              |
| `ninja`        | Build backend                       |
| `cxxopts`      | C++ command line option parser      |
| `rapidjson`    | JSON parsing                        |
| `tomlplusplus` | TOML configuration parsing          |

## Build System

### Build Process

Xenia Canary uses a **custom Python-based build system** (`xenia-build`) that wraps:

- **CMake** for project configuration
- **Ninja** for actual compilation

### Build Commands

```bash
# Configure
./xenia-build premake

# Build release
./xenia-build build --config release
```

### Environment Variables

The xenia-build script automatically uses these environment variables:

| Variable     | Purpose                    | Default       |
| ------------ | -------------------------- | ------------- |
| `CC`         | C compiler                 | `clang`       |
| `CXX`        | C++ compiler               | `clang++`     |
| `PKGCONFIG`  | Path to pkg-config binary  | `pkg-config`  |
| `SDL2CONFIG` | Path to sdl2-config binary | `sdl2-config` |

**Note**: No patch is needed for CC/CXX - the upstream script already uses `os.environ.get("CC", "clang")` in the `run_cmake_configure()` function.

## Patches

### Required Patches

| Patch                                     | Purpose                                                                                                                                                                                                                                                              |
| ----------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `001-disable-lto-lld-cross-compile.patch` | Disables LTO (Link Time Optimization) and lld linker for cross-compilation. LTO requires LLVMgold.so which is not available. The lld linker is not available in the Buildroot cross-compilation toolchain, so the system linker (ld.bfd or ld.gold) is used instead. |
| `002-fix-python3-compile-shader.patch`    | Fixes two issues in compile_shader_spirv.py: 1) Python 3 compatibility - stderr is bytes but Python 3 expects strings. 2) Removes unsupported `--canonicalize-ids` flag from spirv-opt (not available in older SPIRV-Tools versions).                                |

### Removed Patches

The following patches have been removed as they are no longer needed:

| Patch                                 | Reason                                                       |
| ------------------------------------- | ------------------------------------------------------------ |
| `000-fix-pkgconfig-lua.patch`         | No longer needed - xenia-build.py uses environment variables |
| `001-hack-force-stdlibs.patch`        | No longer needed - build system handles stdlibs correctly    |
| `002-linux-hid-keyboard-driver.patch` | WIP feature, not needed for basic emulation                  |
| `001-disable-lto-cross-compile.patch` | Merged into `001-disable-lto-lld-cross-compile.patch`        |
| `003-disable-lld-linker.patch`        | Merged into `001-disable-lto-lld-cross-compile.patch`        |

## Installation Paths

| Path                               | Content                                    |
| ---------------------------------- | ------------------------------------------ |
| `/usr/bin/xenia_canary`            | Main emulator binary                       |
| `/usr/share/xenia-canary/patches/` | Game compatibility patches (`.toml` files) |

## Known Issues

### Build Issues

1. **Clang mandatory**: GCC is not easily interchangeable; Clang is required for shader compilation.

2. **Vulkan required**: Must have working Vulkan drivers (NVIDIA proprietary, AMD RADV, or Intel ANV).

3. **LTO and lld disabled**: Link Time Optimization is disabled for cross-compilation (LLVMgold.so not available). The lld linker is also disabled; the system linker (ld.bfd or ld.gold) is used instead.

### Runtime Issues

1. **GTK3 required**: Cannot build headless; GTK3 is used for window management and Dear ImGui clipboard integration.

2. **Shader compilation**: First-time shader compilation can cause significant stuttering.

3. **x86_64 only**: The emulator uses x86_64 JIT compilation (Xbyak) and cannot run on ARM/AArch64/RISC-V.

## Notes

1. **Dear ImGui**: The UI uses Dear ImGui rendered on top of Vulkan, with GTK3 providing the windowing backend.

2. **D3D12→Vulkan**: VKD3D-Proton translation allows D3D12 games to run on Vulkan (Linux).

3. **Shader cache**: Shaders are compiled at runtime; consider pre-compiling for frequently played games.

4. **Audio**: Uses SDL2 for audio output; ALSA backend is available on Linux.

5. **Discord Rich Presence**: Optional feature (can be disabled at build time).

## References

- **Official Website**: https://xenia.jp/
- **GitHub**: https://github.com/xenia-canary/xenia-canary
- **Building Documentation**: https://github.com/xenia-canary/xenia-canary/blob/canary_experimental/docs/building.md
- **AUR Package**: https://aur.archlinux.org/packages/xenia-canary-git
