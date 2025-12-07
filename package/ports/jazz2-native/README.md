# Jazz² Native

Rebuild of the Jazz Jackrabbit 2 engine using modern SDL/OpenAL tooling.

## Build notes
- **Version:** 3.4.0 from `deathkiller/jazz2-native`, built with git submodules.
- **Config:** selects SDL2, OpenAL, libopenmpt, zlib, libcurl, and optionally `libgl`, `libglew`, `libglfw` when X11 with GL is available.
- **Build system:** CMake release build with `NCINE` backend options; switches between GLFW and SDL2 renderers and forces GLES when no desktop GL is present.
- **Extras:** copies `jazz2.keys` into `/usr/share/evmapy`.
