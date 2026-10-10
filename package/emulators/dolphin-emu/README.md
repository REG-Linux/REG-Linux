# dolphin-emu

GameCube and Wii emulator. Upstream: https://github.com/dolphin-emu/dolphin

## Build Configuration

Qt6 frontend enabled when `BR2_PACKAGE_REGLINUX_HAS_QT6` is set, otherwise NoGUI mode.
Vulkan, X11, and Wayland are conditionally enabled based on package selection.

## Audio Backend

This package uses **cubeb** as the default audio backend for low-latency audio playback.
ALSA and PulseAudio backends are disabled by default to reduce dependencies.

## Dependencies

### Required

- `cubeb` - Audio I/O library (Mozilla)
- `libdrm` - Direct Rendering Manager support
- `ffmpeg` - Video/audio decoding and frame dumping
- `sdl2` / `sdl3` - Input and audio support
- `libevdev` - Linux input event handling
- `bluez5_utils` - Bluetooth support
- `hidapi` - HID device support

### Optional

- `reglinux-qt6` - Qt6 GUI frontend (when `BR2_PACKAGE_REGLINUX_HAS_QT6=y`)
- `wayland` / `wayland-protocols` / `libdecor` - Wayland support
- `xlib_libXi` - X11 input extension
- `vulkan-headers` / `vulkan-loader` - Vulkan renderer (when `BR2_PACKAGE_REGLINUX_VULKAN=y`)

## Disabled Features

The following features are disabled to reduce build size and dependencies:

- Analytics
- Auto-update
- Discord RPC
- CLI tool
- MGBA integration
- UPnP
- Tests
- ALSA backend (using cubeb instead)
- PulseAudio backend (using cubeb instead)

## Patches

This package includes several REG-Linux specific patches:

- **001-padorder.patch**: Sorts controller devices for consistent ordering
- **002-fix-libipc-include.patch**: Fixes libipc include paths for cross-compilation
- **003-hide-osd-msg.patch**: Hides verbose OSD video info messages
- **004-nicerlaunch.patch**: Hides UI elements on game launch for cleaner experience
- **005-guns.patch**: Adds light gun support with aspect ratio correction
- **006-customtextures.patch**: Adds custom textures path configuration
- **007-disable-events-merging.patch**: Disables event merging for input
- **008-bios-location.patch**: Changes BIOS location to `/userdata/bios/GC/`
- **011-savestate-with-romname.patch**: Uses ROM name for savestate files
- **1003-fix-libmali.patch**: Fixes libmali linking for embedded systems
