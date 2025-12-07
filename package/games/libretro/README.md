# Libretro game ports

Contains game-specific libretro cores that REG-Linux builds alongside the engine packages.

- `libretro-mrboom/`: builds the `mrboom_libretro.so` core with NEON detection and GLES-friendly flags.
- `libretro-superbroswar/`: builds the `superbroswar_libretro.so` core for the Super Mario War reimplementation.

Both packages require a C++ toolchain; consult each subdirectory README for platform overrides, patches, and install targets.
