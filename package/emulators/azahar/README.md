# Azahar

**Nintendo 3DS emulator (Citra fork)**

Upstream: https://github.com/azahar-emu/azahar

## Version

- **Current**: 2124.3 (git)

## Architecture Support

| Architecture | Status    | Notes                            |
| ------------ | --------- | -------------------------------- |
| **x86_64**   | ✅ Stable | Primary target                   |
| **aarch64**  | ✅ Stable | ARM64 devices (Steam Deck, etc.) |

## Dependencies

### Mandatory

| Package   | Purpose               |
| --------- | --------------------- |
| `fmt`     | Formatting library    |
| `boost`   | C++ utilities         |
| `ffmpeg`  | Video decoding        |
| `sdl2`    | Input/windowing       |
| `fdk-aac` | AAC audio decoding    |
| `cubeb`   | Audio backend         |
| `openssl` | Cryptography/network  |
| `libzip`  | ZIP archive support   |
| `lz4`     | Compression           |
| `zstd`    | Zstandard compression |
| `reglinux-qt6` | Qt6 frontend     |

### Conditional

| Package             | Purpose                | Config Option                  |
| ------------------- | ---------------------- | ------------------------------ |
| `vulkan-headers`    | Vulkan support         | `BR2_PACKAGE_REGLINUX_VULKAN`  |
| `vulkan-loader`     | Vulkan runtime         | `BR2_PACKAGE_REGLINUX_VULKAN`  |
| `xwayland`          | X11 compatibility      | `BR2_PACKAGE_XWAYLAND`         |
| `wayland`           | Wayland display server | `BR2_PACKAGE_WAYLAND`          |
| `wayland-protocols` | Wayland protocols      | `BR2_PACKAGE_WAYLAND`          |

## Build Configuration

### CMake Options

```cmake
-DCMAKE_BUILD_TYPE=Release
-DBUILD_SHARED_LIBS=OFF
-DENABLE_SDL2=ON
-DENABLE_CUBEB=ON
-DENABLE_OPENAL=OFF
-DENABLE_QT=ON
-DENABLE_VULKAN=ON/OFF
-DENABLE_SSE42=ON/OFF (x86_64_v3 only)
```

### Audio Backend

Azahar uses **cubeb** as the audio backend (OpenAL disabled by default).

### Frontends

- **Qt6** is the only frontend. Upstream dropped the SDL2 one: the `azahar` binary
  (`citra_meta`) is only built with `ENABLE_QT`, so `reglinux-qt6` is always a dependency.
  SDL2 is still used for input.

## Patches

### Active Patches

| Patch                                 | Purpose                               | Status    |
| ------------------------------------- | ------------------------------------- | --------- |
| `001-fix-src-common-settings-h.patch` | Fix X11 `None` macro conflict         | ✅ Active |
| `002-fix-qt6.10.patch`                | Fix Qt6.10 compatibility (GuiPrivate) | ✅ Active |

## Installation

### Target Paths

```
/usr/bin/
└── azahar                    # Main executable
```

### Config Path

Azahar uses standard XDG directories:

```
/userdata/azahar/
├── config/
├── cache/
├── logs/
└── saves/
```

## Testing

### Build Test

```bash
make azahar
make azahar-dirclean
make azahar-rebuild
```

### Runtime Test

```bash
# Start Azahar
azahar

# Fullscreen
azahar --fullscreen
```

## Known Issues

1. **SSE 4.2**: Only enabled on `x86_64_v3` builds. Older x86_64 CPUs may require building from source with `-DENABLE_SSE42=OFF`.

2. **Vulkan**: Requires both `BR2_PACKAGE_XWAYLAND` and `BR2_PACKAGE_REGLINUX_VULKAN`.

3. **Audio**: Uses cubeb backend. Ensure audio is working on your system before troubleshooting emulator audio.

## References

- **GitHub**: https://github.com/azahar-emu/azahar
- **Based on**: Citra (https://github.com/citra-emu/citra)

## Maintainer Notes

### Updating Version

1. Update `AZAHAR_VERSION` in `azahar.mk`
2. Test build with `make azahar-rebuild`
3. Verify runtime with test ROMs

### Removing Patches

Check upstream regularly for fixes that have been merged:

```bash
cd azahar
git log --oneline --grep="settings\|qt\|cmake"
```

Remove patches that have been upstreamed.
