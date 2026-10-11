# mupen64plus-ui-console

Console (command-line) user interface for Mupen64Plus. Upstream: https://github.com/mupen64plus/mupen64plus-ui-console

## Build Configuration

This package uses the Buildroot generic-package infrastructure with custom build commands.
It requires `mupen64plus-core` to be built first.

## Dependencies

### Required

- `sdl2` - Required dependency (inherited from core)
- `alsa-lib` - Required dependency (inherited from core)
- `mupen64plus-core` - Core emulator library

## Features

This package provides:

- Command-line interface for running Mupen64Plus
- No graphical frontend required
- Suitable for headless or minimal setups
- Full emulator control through command-line options

## Installation

The console UI is installed to:

- `/usr/bin/mupen64plus`

## Usage

```bash
# Run a ROM
mupen64plus /path/to/rom.z64

# Run with specific options
mupen64plus --noosd --noask /path/to/rom.z64
```

## Configuration

Configuration files are located in:

- `/usr/share/mupen64plus/mupen64plus.ini` - Main configuration
- `/usr/share/mupen64plus/InputAutoCfg.ini` - Controller mappings

User configuration is stored in:

- `~/.local/share/mupen64plus/`

## Notes

- This is a minimal frontend suitable for embedded systems
- For graphical frontend, consider using mupen64plus-qt or similar
- Works well with controller-based navigation
