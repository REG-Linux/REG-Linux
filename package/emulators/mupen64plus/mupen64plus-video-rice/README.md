# mupen64plus-video-rice

Rice Video video plugin for Mupen64Plus. Upstream: https://github.com/mupen64plus/mupen64plus-video-rice

## Build Configuration

This package uses the Buildroot generic-package infrastructure with custom build commands.
It requires `mupen64plus-core` to be built first.

## Dependencies

### Required

- `sdl2` - Window/input handling
- `alsa-lib` - Audio (inherited)
- `mupen64plus-core` - Core emulator library
- `boost` - C++ libraries

## Graphics Features

Rice Video provides:

- Fast OpenGL rendering
- Good compatibility with many games
- Based on the RiceVideoLinux plugin from earlier versions
- Texture enhancement support

## Installation

The plugin is installed to:

- `/usr/lib/mupen64plus/mupen64plus-video-rice.so`

## Configuration

Rice Video settings are configured in:

- `/usr/share/mupen64plus/RiceVideo.cfg`

## Notes

- This plugin is based on the RiceVideoLinux plugin from earlier versions
- Provides fast rendering with good compatibility
- Less demanding than GLideN64
- Suitable for lower-end hardware or games that work well with Rice
