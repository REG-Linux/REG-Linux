# Raze (Build Engine front end)

GZDoom-based port for classic Build Engine games (Duke Nukem 3D, Shadow Warrior, Blood, etc.).

## Build notes
- **Version:** 1.11.0 release built with host/target CMake builds.
- **Config:** selects SDL2, SDL2_net/mixer, libjpeg, OpenAL, ZMusic, WebP, libvpx, optional Vulkan, and musl helpers; also depends on `host-sdl2` to build `ImportExecutables.cmake`.
- **Build system:** CMake release build with `FORCE_CROSSCOMPILE`, toggled Vulkan (depending on `vulkan-*` packages), and GLES2 fallback when desktop GL is absent. The host build is added to satisfy `IMPORT_EXECUTABLES`.
- **Extras:** installs the binary, PK3s, soundfonts, and `raze.keys` for evmapy; included build removes GUI dependencies by disabling Vulkan when not available.
