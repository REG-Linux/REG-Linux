# EasyRPG-related packages

The `easyrpg` subtree keeps the EasyRPG interpreter and its helper library that parse RPG Maker 2000/2003 data. The two Buildroot recipes expose the packages defined under this folder.

## liblcf
- **Purpose:** Provides the LCF data parser shared by the player and libretro core.
- **Config summary:** selects `expat`, `ICU`, and `inih` so the library can read both LCF and XML game data.
- **Build info:** CMake-based build (v0.8.1), installs both shared and static variants and stages the library because the player links against it.

## easyrpg-player
- **Purpose:** EasyRPG Player itself, an interpreter for RPG Maker 2000/2003 and native EasyRPG games.
- **Config summary:** pulls in SDL2, SDL2_mixer, libpng, fmt, mpg123, libvorbis, opusfile, pixman, speexdsp, libxmp, wildmidi, json-for-modern-cpp, libsndfile, lhasa, and the `liblcf` library.
- **Build info:** CMake build (v0.8.1.1) that enables both shared and static builds, links against staged `liblcf`, and runs the `easyrpg.easyrpg.keys` file into `/usr/share/evmapy` during install.
