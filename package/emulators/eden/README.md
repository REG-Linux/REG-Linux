# eden

Nintendo Switch emulator (Yuzu/Citra fork). Upstream: https://git.eden-emu.dev/eden-emu/eden

## Build Configuration

Requires Qt6 and SDL2. Architecture-specific options are set for ARM64 and x86_64.
`host-yasm` is added on x86_64 for ASM optimizations.

## Audio Backend

This package uses **cubeb** as the default audio backend for low-latency audio playback.

## Dependencies

### Required

- `cubeb` - Audio I/O library (Mozilla)
- `libdrm` - Direct Rendering Manager support
- `wayland` / `libxkbcommon` - Wayland input support
- `reglinux-qt6` - Qt6 GUI frontend
- `sdl2` - Input and audio support
- `fmt` - Formatting library
- `boost` - C++ libraries
- `zstd` / `zlib` / `lz4` / `libzip` - Compression libraries
- `catch2` - Testing framework
- `opus` - Audio codec
- `enet` - Network library
- `json-for-modern-cpp` - JSON library
- `libva` - Video acceleration
- `libusb` - USB device access
- `ffmpeg` - Video/audio decoding
- `mbedtls` - Cryptography library
- `gamemode` - Game mode support

### Optional

- `xwayland` - X11 compatibility layer (when `BR2_PACKAGE_XWAYLAND=y`)
- `vulkan-headers` / `vulkan-loader` / `host-glslang` - Vulkan renderer (when `BR2_PACKAGE_REGLINUX_VULKAN=y`)
- `host-yasm` - YASM assembler (x86_64 only)

## Disabled Features

The following features are disabled to reduce build size and dependencies:

- Discord Rich Presence
- Tests (EDEN_TESTS)
- Sanitizers
- Bundled FFmpeg (uses system version)
- External SDL2 (uses system version)
- CPM package manager (uses system libraries)

## Patches

This package includes several REG-Linux specific patches:

- **001-fix-sse2neon.patch**: Fixes SSE2NEON conversion warnings on ARM
- **002-adjust-paths.patch**: Changes data paths to REG-Linux locations:
    - Keys: `/userdata/bios/switch`
    - Logs: `/userdata/system/logs`
    - Screenshots: `/userdata/screenshots/switch/eden`
- **003-external-nx-tzdb-prebuilt.patch**: Uses external timezone database
- **004-format_custom.patch**: Custom format fixes
