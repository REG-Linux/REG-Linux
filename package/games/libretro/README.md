# Libretro game ports

This folder holds game-specific libretro cores that REG-Linux cross-compiles alongside the standalone engine packages. Each core builds a single `.so` that the frontend loads, so the README inside the core’s directory documents the version, dependencies, build helper, and install artifacts specific to that libretro package.

## Core summaries
- `libretro-mrboom/`: builds `mrboom_libretro.so`, applying NEON detection and GLES-friendly linker flags so the retro Bomberman-style game behaves on ARM consoles.
- `libretro-superbroswar/`: compiles `superbroswar_libretro.so` for the Super Mario War reimplementation, shipping the patched build that handles modern GCC and libstdc++ toggles.
