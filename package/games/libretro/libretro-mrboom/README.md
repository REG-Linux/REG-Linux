# Libretro Mr. Boom

The `libretro-mrboom` core supplies REG-Linux with the Mr. Boom Bomberman-style experience, detecting NEON on ARM and leaving `mrboom_libretro.so` ready for RetroArch frontends.

## Build notes

- `Version`: 5.5 release (May 2024) from `Javanaise/mrboom-libretro`.
- `Dependencies`: `BR2_INSTALL_LIBSTDCPP`, NEON detection on ARM; `SKIP_GIT=1` for cross-builds.
- `Build helper`: Generic/Makefile (`generic-package`) that invokes the upstream Makefile and installs `/usr/lib/libretro/mrboom_libretro.so`.
