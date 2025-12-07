# OpenMW (Morrowind engine)

Cross-compiles the OpenMW project with a heavily trimmed CMake profile for REG-Linux.

## Build notes
- **Version:** `stable` from `OpenMW/openmw` (git).
- **Config:** requires desktop GL (`BR2_PACKAGE_HAS_LIBGL`) and X11 (`BR2_PACKAGE_XORG7`), plus dependencies like Cairo, SDL2, Boost, Bullet, ffmpeg, YAML-CPP, Lua, Fontconfig, FreeType, and optionally LuaJIT.
- **Build system:** CMake release build that disables docs, tools, launcher, OpenCS, wizards, and exports, enables LTO, forces mono install prefix, and uses custom `OSG_WINDOWING_SYSTEM` (X11 when available).
- **Extras:** none beyond the default CMake install target.
