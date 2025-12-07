# EasyRPG Player

This package builds the EasyRPG Player interpreter for RPG Maker 2000/2003 and EasyRPG games.

## Build configuration
- **Version:** 0.8.1.1, pulled from the official EasyRPG GitHub release.
- **Config selections:** requires `liblcf`, SDL2, SDL2_mixer, fmt, mpg123, libvorbis, opusfile, pixman, speexdsp, libxmp, wildmidi, json-for-modern-cpp, libsndfile, and lhasa. Optional `harfbuzz`/`fluidsynth` are added when available.
- **Build system:** CMake with both shared and static targets enabled; uses PIC flags to keep the interpreter relocatable.
- **Post-install:** copies `easyrpg.easyrpg.keys` into `/usr/share/evmapy` for the REG-Linux front-end.
