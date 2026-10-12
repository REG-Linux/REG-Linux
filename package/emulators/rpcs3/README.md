# rpcs3

PlayStation 3 emulator. Upstream: https://github.com/RPCS3/rpcs3

## Build Configuration

Requires LLVM and Qt6. The following options are set for cross-compilation:

- `-DUSE_NATIVE_INSTRUCTIONS=OFF` - Disable native CPU instructions
- `-DSTATIC_LINK_LLVM=OFF` - Use shared LLVM library
- `-DUSE_SYSTEM_*` - Use system libraries instead of bundled copies

## Audio Backend

This package uses **cubeb** as the default audio backend for low-latency audio playback.
OpenAL is also available as an alternative backend.

## Dependencies

### Required

- `cubeb` - Audio I/O library (Mozilla)
- `libdrm` - Direct Rendering Manager support
- `wayland` / `libxkbcommon` - Wayland input support
- `llvm` - LLVM compiler infrastructure
- `ffmpeg` - Video/audio decoding
- `sdl3` - Input and audio support
- `libevdev` - Linux input event handling
- `reglinux-qt6` - Qt6 GUI frontend
- `mesa3d` - OpenGL implementation
- `libglu` - OpenGL Utility Library
- `libglew` - OpenGL Extension Wrangler
- `openal` - Alternative audio backend
- `alsa-lib` - ALSA audio support
- `libcurl` - URL transfer library
- `libusb` - USB device access
- `libxml2` - XML parsing
- `pugixml` - XML library
- `rtmidi` - MIDI I/O library
- `rtmpdump` - RTMP streaming
- `zlib` / `zstd` - Compression libraries
- `ncurses` - Terminal UI

### Optional

- `vulkan-headers` / `vulkan-loader` - Vulkan renderer (when `BR2_PACKAGE_REGLINUX_VULKAN=y`)

## Disabled Features

The following features are disabled to reduce build size and dependencies:

- Native CPU instructions (for cross-compilation compatibility)
- Static LLVM linking (uses shared library instead)
- WolfSSL (using alternative SSL implementation)
- Precompiled headers (for cleaner builds)

## Patches

This package includes several REG-Linux specific patches:

- **001-fix-libusb.patch**: Fixes libusb include path for cross-compilation
- **004-fix-iconv.patch**: Fixes iconv detection for cross-compilation
- **006-no-firmware-confirmation.patch**: Skips firmware confirmation dialogs
- **007-fix-screenshot-directory.patch**: Changes screenshot save location
- **010-padsevdev.patch**: Fixes evdev device naming for consistent controller ordering
- **012-savestate-location.patch**: Changes savestate location to `/userdata/saves/ps3/`
- **013-gun-support.patch**: Adds light gun support via udev property matching
- **014-gun-mapping.patch**: Adds gun input mapping for light gun peripherals
