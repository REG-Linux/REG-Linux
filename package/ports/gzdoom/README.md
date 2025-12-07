# GZDoom

Modern Doom source port from the ZDoom project with optional Vulkan/GLES support.

## Build notes
- **Version:** g4.14.2 release (May 2025) built with `host-gzdoom` and `host-webp`/`host-zmusic` helper packages.
- **Config:** selects SDL2, SDL2_net/mixer, libjpeg, GL/OpenAL, ZMusic, WebP, libvpx, and musl helpers; Vulkan support is gated on the presence of `vulkan-headers`, `vulkan-loader`, and optional Wayland/X11.
- **Build system:** CMake release build with cross-compile flags, `ImportExecutables.cmake`, and `-DHAVE_VULKAN` toggling; adds a post-patch hook that forces GLES2 support when desktop GL is unavailable so the game can run purely on GLES.
- **Extras:** installs the binary plus PK3s, raw banks, and soundfonts under `/usr/share/gzdoom`, and copies `gzdoom.keys` into `/usr/share/evmapy`.
