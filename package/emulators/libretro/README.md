# Libretro cores maintained as emulator targets

This folder organizes the libretro cores that REG-Linux cross-compiles alongside the standalone emulators. Each subdirectory (e.g., `libretro-mame`, `libretro-flycast`, `libretro-beetle-pcfx`, `libretro-snes9x`, etc.) contains its own `Config.in`, `.mk`, and README describing the selected dependencies and build helper. The shared layout picks up the standard libretro build helpers, patches, and placement of the `.so` under `/usr/lib/libretro`.

Browse a specific core README to see its version, config selections, and any key/patch assets that accompany the build.
