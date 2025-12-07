# OpenBOR 4432

`openbor4432` builds the legacy `v3b4432` fork from the `Darknior/OpenBORv3b4432` repository with the SDL2 stack and libvpx/vorbis codecs that REG-Linux requires.

## Configuration
- **Config selection:** selects `libvpx`, `SDL2`, `SDL2_gfx`, `libpng`, `libogg`, and `libvorbis`.
- **Version:** Git commit `38855f23a4637eda3c9ba7dfa057fd2cf8434de1`.
- **Build flow:** runs the shipped `version.sh` to set the release ID and then calls `make` with architecture-specific `BUILD_*` flags (x86_64, ARM, MIPS, RISC-V). Installs `OpenBOR4432` under `/usr/bin`.

## Patches delivered in this folder
- `0001-Fix-anim_list-and-model_cache-definitions.patch`
- `001-x86_64.patch`
- `002-fixkeys.patch`
- `003-arm.patch`
- `004-gccoptions.patch`
- `005-sdl2gfx.patch`
- `006-axismanagement.patch`
- `007-fix-pad-axis-combos-player-running.patch`
