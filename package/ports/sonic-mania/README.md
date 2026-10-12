# Sonic Mania

Sonic Mania decompilation port. Upstream: https://github.com/RSDKModding/Sonic-Mania-Decompilation

## Build Configuration

- **Subsystem**: SDL2
- **Static build**: Yes (`GAME_STATIC=ON`)
- **Editor**: Disabled (`GAME_INCLUDE_EDITOR=OFF`)
- **Output name**: `sonic-mania`

## Dependencies

- **Required**: sdl2, libogg, libtheora
- **Optional (X11/Xorg)**: libglu, libglew, libglfw

## CMake Options

| Option                | Value          | Description              |
| --------------------- | -------------- | ------------------------ |
| `RETRO_SUBSYSTEM`     | `SDL2`         | SDL2 subsystem           |
| `GAME_STATIC`         | `ON`           | Static build             |
| `GAME_INCLUDE_EDITOR` | `OFF`          | Exclude editor functions |
| `WITH_RSDK`           | `ON` (default) | Build with RSDKv5        |

## Notes

- Requires assets from the official Sonic Mania (Plus) game (not included)
- Git submodules are required (`SONIC_MANIA_GIT_SUBMODULES = YES`)
- On Xorg systems, additional GL dependencies are pulled in automatically
- Uses PipeWire audio backend via SDL2 on REG-Linux
