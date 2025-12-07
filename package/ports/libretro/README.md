# Libretro ports

This folder mirrors the additional libretro cores distributed as ports rather than engines.
Each subdirectory builds a single `.so` core that REG-Linux can drop into `/usr/lib/libretro`.

## Cores
- `libretro-nxengine`: Cave Story (NXEngine) core that adapts NSE/NEON targets.
- `libretro-prboom`: ARM-ready Doom core with runtime `GIT_VERSION` stamping.
- `libretro-reminiscence`: Flashback reimplementation packaged as a libretro module.
- `libretro-tyrquake`: Quake I core with platform-specific flags for Raspberry Pi boards.
- `libretro-xrick`: Rick Dangerous core.
- `libretro-zc210`: Zelda Classic core with git-based version stamping.

Each package takes the standard libretro build helper and defines `LIBRETRO_PLATFORM` per target; refer to the individual subfolder README for more details.
