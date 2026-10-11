# mupen64plus-input-sdl

Input plugin for Mupen64Plus using SDL. Upstream: https://github.com/mupen64plus/mupen64plus-input-sdl

## Build Configuration

This package uses the Buildroot generic-package infrastructure with custom build commands.
It requires `mupen64plus-core` to be built first.

## Dependencies

### Required

- `sdl2` - Input handling through SDL
- `alsa-lib` - Required dependency (inherited from core)
- `mupen64plus-core` - Core emulator library

## Input Support

This plugin provides:

- Gamepad/controller support through SDL
- Keyboard input mapping
- Analog stick emulation
- Rumble feedback support

## Installation

The plugin is installed to:

- `/usr/lib/mupen64plus/mupen64plus-input-sdl.so`

## Configuration

Input settings are configured in `/usr/share/mupen64plus/InputAutoCfg.ini`:

- Controller mappings
- Button configurations
- Axis mappings

## Notes

- This plugin is derived from the original Mupen64 blight_input plugin
- Uses SDL2 for cross-platform input handling
- Supports multiple controllers simultaneously
