# vita3k

**PlayStation Vita emulator**

Upstream: https://github.com/Vita3K/Vita3K

## Version

- **Commit**: `750a516d8fb8ffaaa063db3d226d8f382db58063` (build 3912, January 28, 2026)
- **SDL Version**: SDL3 (migrated since build 3806)

## Dependencies

### Runtime Dependencies

| Package              | Purpose                                           |
| -------------------- | ------------------------------------------------- |
| `sdl3`               | Cross-platform multimedia (input, display, audio) |
| `sdl3_image`         | Image loading support                             |
| `sdl3_ttf`           | TrueType font rendering                           |
| `zlib`               | Compression library                               |
| `libogg`             | Ogg container format support                      |
| `libvorbis`          | Vorbis audio decoding                             |
| `boost`              | C++ utility libraries                             |
| `python-ruamel-yaml` | YAML parsing (configuration files)                |
| `fmt`                | Fast formatting library                           |
| `libcurl`            | Network transfers (shader cache, etc.)            |

### Removed Dependencies

- **`libgtk3`**: Not required - Vita3K uses ImGui + SDL3 for its UI, not GTK
- **`sdl2`/`sdl2_image`/`sdl2_ttf`**: Migrated to SDL3 since build 3806 (October 2025)

## Build Configuration

### CMake Options

```cmake
-DCMAKE_BUILD_TYPE=Release
-DBUILD_SHARED_LIBS=OFF
-DUSE_DISCORD_RICH_PRESENCE=OFF
-DUSE_VITA3K_UPDATE=OFF
-DBUILD_EXTERNAL=OFF
```

### x86_64-v3 Optimization

On x86_64_v3 targets, `-DXXH_X86DISPATCH_ALLOW_AVX=ON` is set for wider xxHash dispatch paths using AVX instructions.

## Patches

| Patch                           | Purpose                                                                          |
| ------------------------------- | -------------------------------------------------------------------------------- |
| `001-adjust-paths.patch`        | Redirects save/config paths to REG Linux conventions (`/userdata/saves/psvita/`) |
| `004-lower-case-vita.patch`     | Changes app name from "Vita3K" to "vita3k" for consistency                       |
| `005-fix-header.patch`          | Fixes missing header includes                                                    |
| `006-hack-ffmpeg-git-sha.patch` | Works around FFmpeg version detection                                            |

**Removed Patches:**

| Patch                          | Reason                                                                 |
| ------------------------------ | ---------------------------------------------------------------------- |
| `003-disable-nfd-portal.patch` | Removed - Upstream uses NFD_PORTAL=ON by default, set via CMake option |

## Installation Path

Binary and data files are installed to:

```
/usr/bin/vita3k/
```

## Data Paths (REG Linux)

- **Save data**: `/userdata/saves/psvita/`
- **Configuration**: `~/.config/vita3k/` or `$XDG_CONFIG_HOME/vita3k/`
- **Cache**: `$XDG_CACHE_HOME/vita3k/`

## Notes

1. **No GUI toolkit dependency**: Vita3K uses Dear ImGui for its UI, rendered via SDL3 + OpenGL/Vulkan
2. **nativefiledialog**: Uses xdg-desktop-portal (D-Bus) instead of GTK via `-DNFD_PORTAL=ON` CMake option
3. **Git submodules**: Required (`VITA3K_GIT_SUBMODULES=YES`) for external libraries (ImGui, glslang, SPIRV-Cross, etc.)
4. **Vulkan support**: Ensure Mesa Vulkan drivers are available for your GPU (PanVK for Mali, RADV for AMD, ANV for Intel)

## Known Issues

- **Motion controls**: May require additional controller configuration (SDL3 migration introduced some regressions)
- **Camera support**: SDL3 camera API is experimental on embedded platforms
