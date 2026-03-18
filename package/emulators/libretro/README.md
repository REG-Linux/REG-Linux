# emulators/libretro

Libretro cores built as emulator targets. Each subdirectory produces a single `.so` core installed under `/usr/lib/libretro/`. All cores share the standard libretro build helpers; per-platform `LIBRETRO_PLATFORM` values and any architecture-specific flags are set individually in each package's `.mk`.
