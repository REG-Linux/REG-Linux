# mupen64plus-video-glide64mk2

Glide64mk2 video plugin for Mupen64Plus. Upstream: https://github.com/mupen64plus/mupen64plus-video-glide64mk2

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

Glide64mk2 provides:

- Glide API emulation
- Good compatibility with many games
- Based on gonetz's 10th anniversary release
- OpenGL rendering

## Installation

The plugin is installed to:

- `/usr/lib/mupen64plus/mupen64plus-video-glide64mk2.so`

## Configuration

Glide64mk2 settings are configured in:

- `/usr/share/mupen64plus/glide64mk2.ini`

## Notes

- This plugin is based on the 10th anniversary release code from gonetz
- Provides good compatibility for games that use the Glide API
- Less demanding than GLideN64 but with fewer features
- Suitable for lower-end hardware
