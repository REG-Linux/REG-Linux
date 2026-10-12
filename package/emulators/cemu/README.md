# Cemu

**Wii U emulator**

Upstream: https://github.com/cemu-project/Cemu

## Version

- **Current**: a04eb53822d306435f4efaba36225bc3bd297f5d (git)
- **Status**: Unstable (WIP aarch64 support)

## Architecture Support

| Architecture | Status    | Notes                                                          |
| ------------ | --------- | -------------------------------------------------------------- |
| **x86_64**   | ✅ Stable | Primary target (desktop PCs)                                   |
| **aarch64**  | ⚠️ WIP    | Requires `-flax-vector-conversions` (Linux ARM, Apple Silicon) |

## Dependencies

### Mandatory

| Package        | Purpose                      |
| -------------- | ---------------------------- |
| `sdl2`         | Input/audio/windowing        |
| `pugixml`      | XML parsing                  |
| `rapidjson`    | JSON parsing                 |
| `boost`        | C++ utilities                |
| `libpng`       | PNG image support            |
| `libcurl`      | Network features             |
| `libzip`       | ZIP archive support          |
| `zlib`         | Compression                  |
| `zstd`         | Zstandard compression        |
| `wxwidgets`    | UI framework                 |
| `fmt`          | Formatting library           |
| `glm`          | Math library                 |
| `upower`       | Power management             |
| `libusb`       | USB support                  |
| `bluez5_utils` | Bluetooth/Wiimote            |
| `webp`         | WebP image support           |
| `hidapi`       | HID device support (Wiimote) |
| `glslang`      | Vulkan shader compilation    |

### Conditional

| Package             | Purpose                  | Config Option                 |
| ------------------- | ------------------------ | ----------------------------- |
| `libgl`             | OpenGL backend           | `BR2_PACKAGE_HAS_LIBGL`       |
| `vulkan-headers`    | Vulkan support           | `BR2_PACKAGE_REGLINUX_VULKAN` |
| `vulkan-loader`     | Vulkan runtime           | `BR2_PACKAGE_REGLINUX_VULKAN` |
| `wayland`           | Wayland display server   | `BR2_PACKAGE_WAYLAND`         |
| `wayland-protocols` | Wayland protocols        | `BR2_PACKAGE_WAYLAND`         |
| `gamemode`          | Performance optimization | `BR2_PACKAGE_GAMEMODE`        |

### Host Tools

| Package        | Purpose                         |
| -------------- | ------------------------------- |
| `host-pugixml` | XML parsing (build host)        |
| `host-glslang` | Shader compilation (build host) |
| `host-nasm`    | Assembler (build host)          |
| `host-zstd`    | Compression (build host)        |
| `host-libusb`  | USB tools (build host)          |

### TODO

None — all dependencies are packaged.

## Build Configuration

### CMake Options

```cmake
-DCMAKE_BUILD_TYPE=Release
-DBUILD_SHARED_LIBS=OFF
-DENABLE_DISCORD_RPC=OFF
-DENABLE_VCPKG=OFF
-DUNIX=ON
-DENABLE_SDL=ON
-DENABLE_CUBEB=ON
-DENABLE_BLUEZ=ON
```

### Graphics Backend

| Backend    | Flag                 | Dependency      |
| ---------- | -------------------- | --------------- |
| **OpenGL** | `-DENABLE_OPENGL=ON` | `libgl`         |
| **Vulkan** | `-DENABLE_VULKAN=ON` | `vulkan-loader` |

### Platform Features

| Feature      | Flag                         | Dependency                     |
| ------------ | ---------------------------- | ------------------------------ |
| **Wayland**  | `-DENABLE_WAYLAND=ON`        | `wayland`, `wayland-protocols` |
| **HIDAPI**   | `-DENABLE_HIDAPI=ON`         | `hidapi`                       |
| **GameMode** | `-DENABLE_FERAL_GAMEMODE=ON` | `gamemode`                     |

## Patches

### Active Patches

| Patch                                      | Purpose                                | Status    |
| ------------------------------------------ | -------------------------------------- | --------- |
| `001-fix_ELFSymboltable.patch`             | Fix ELF symbol table handling          | ✅ Active |
| `002-use-userdata.patch`                   | Use `/userdata` for config/data        | ✅ Active |
| `004-force-no-menubar.patch`               | Force disable menubar                  | ✅ Active |
| `006-fix-keys-path.patch`                  | Fix key configuration path             | ✅ Active |
| `007-fix-hidapi-include.patch`             | Fix hidapi include path                | ✅ Active |
| `008-add-findhidapi-cmake.patch`           | Add Findhidapi.cmake module            | ✅ Active |
| `009-fix-findwaylandprotocols-cmake.patch` | Fix Wayland protocols detection        | ✅ Active |
| `010-fix-warnings-aarch64.patch`           | Fix aarch64 build warnings (Linux ARM) | ✅ Active |
| `011-fix-apple-aarch64.patch`              | Fix Apple aarch64 (macOS ARM/Silicon)  | ✅ Active |

### Disabled Patches

| Patch                              | Purpose                 | Status                |
| ---------------------------------- | ----------------------- | --------------------- |
| `xxx-opengl-hybrid.patch.disabled` | OpenGL hybrid rendering | Disabled (not needed) |

## Installation

### Target Paths

```
/usr/bin/cemu/
├── cemu                    # Main executable
├── gameProfiles/           # Game profiles
└── resources/              # Resources
```

### Config Path

REG Linux uses `/userdata/cemu/` for user data:

```
/userdata/cemu/
├── settings.xml
├── controllerProfiles/
├── gameProfiles/
├── screenshot/
└── shaderCache/
```

## Known Issues

1. **Audio**: Uses cubeb with ALSA backend (default). Audio device is set to "default" for auto-selection.

2. **aarch64**: Requires `-flax-vector-conversions` flag (handled automatically).
    - Linux aarch64: Patch `010-fix-warnings-aarch64.patch`
    - Apple aarch64: Patch `011-fix-apple-aarch64.patch`

3. **Wayland + OpenGL**: May require patch `999-hotfix-crash-wayland-gl-context.patch` (shared with RetroArch).

## Testing

### Build Test

```bash
make cemu
make cemu-dirclean
make cemu-rebuild
```

### Runtime Test

```bash
# Start Cemu
cemu

# With specific game
cemu /path/to/game.wua
```

## References

- **Official Website**: https://cemu.info/
- **GitHub**: https://github.com/cemu-project/Cemu
- **Build Guide**: https://github.com/cemu-project/Cemu/blob/main/BUILD.md
- **Wiki**: https://wiki.cemu.info/

## Maintainer Notes

### Adding cubeb Support

When cubeb is packaged for Buildroot:

1. Add `select BR2_PACKAGE_CUBEB` to `Config.in`
2. Add `cubeb` to `CEMU_DEPENDENCIES` in `cemu.mk`
3. Test audio playback
4. Update this README

### Removing Patches

Check upstream regularly:

```bash
cd Cemu
git log --oneline --grep="hidapi\|wayland\|aarch64"
```

Remove patches that have been upstreamed.

### Architecture Notes

- **x86_64**: Primary target, most stable
- **aarch64 (Linux)**: Requires `-flax-vector-conversions` (handled by `010-fix-warnings-aarch64.patch`)
- **aarch64 (Apple)**: Apple Silicon (M1/M2/M3) requires additional fixes (`011-fix-apple-aarch64.patch`)
