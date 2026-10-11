# ports/libretro

Libretro cores distributed as ports. Each subdirectory produces a single `.so` core installed under `/usr/lib/libretro/`. Platform detection sets a board-specific `platform` variable (e.g. `rpi1`, `armv neon`, `unix`) passed to each core's upstream Makefile.
