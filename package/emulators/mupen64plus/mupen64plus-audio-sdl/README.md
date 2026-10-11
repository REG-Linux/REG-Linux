# mupen64plus-audio-sdl

Audio plugin for Mupen64Plus using SDL. Upstream: https://github.com/mupen64plus/mupen64plus-audio-sdl

## Build Configuration

This package uses the Buildroot generic-package infrastructure with custom build commands.
It requires `mupen64plus-core` to be built first.

## Dependencies

### Required

- `sdl2` - Audio output through SDL
- `alsa-lib` - ALSA audio backend
- `mupen64plus-core` - Core emulator library

## Audio Backend

This plugin uses SDL for audio output. For lower latency audio, consider using
the cubeb-based audio backend when available.

## Installation

The plugin is installed to:

- `/usr/lib/mupen64plus/mupen64plus-audio-sdl.so`

## Configuration

Audio settings are configured in `/usr/share/mupen64plus/mupen64plus.ini`:

- Audio plugin selection
- Sample rate
- Buffer size
- Volume settings

## Notes

- This plugin is based on the original jttl_audio plugin from Mupen64
- Uses SDL2 for cross-platform audio output
- Requires the core library API headers from staging
