# libretro-hatarib

Atari ST / STE / TT libretro core (HatariB). Upstream: https://github.com/bbbradsmith/hatariB

Uses git submodules and requires `libcapsimage`, `libpng`, `sdl2`, and `zlib`; staging-dir paths for SDL2 and zlib are passed explicitly via `CONF_ENV` rather than discovered by CMake.
