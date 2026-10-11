# mupen64plus-rsp-hle

RSP (Reality Signal Processor) HLE plugin for Mupen64Plus. Upstream: https://github.com/mupen64plus/mupen64plus-rsp-hle

## Build Configuration

This package uses the Buildroot generic-package infrastructure with custom build commands.
It requires `mupen64plus-core` to be built first.

## Dependencies

### Required

- `sdl2` - Required dependency (inherited from core)
- `alsa-lib` - Required dependency (inherited from core)
- `mupen64plus-core` - Core emulator library

## RSP Emulation

This plugin provides High-Level Emulation (HLE) of the Nintendo 64's Reality Signal Processor:

- Fast emulation through HLE techniques
- Compatible with most N64 games
- Based on the original Mupen64 HLE RSP plugin v0.2
- Includes Azimer's HLE code improvements by Hacktarux

## Installation

The plugin is installed to:

- `/usr/lib/mupen64plus/mupen64plus-rsp-hle.so`

## Configuration

RSP settings are configured in `/usr/share/mupen64plus/mupen64plus.ini`:

- RSP plugin selection
- HLE options

## Notes

- HLE provides faster emulation but may be less accurate than LLE
- Some games may require specific RSP settings for optimal compatibility
- This is the default RSP plugin for most configurations
