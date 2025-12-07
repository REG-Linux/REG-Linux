# ioquake3

Community continuation of the Quake III Arena engine with SDL2 and modular codecs.

## Build notes
- **Version:** commit `3d8979f...` from `ioquake/ioq3`.
- **Config:** selects SDL2, SDL2_net, libogg/vorbis, Opus/Opusfile, JPEG, libcurl, and toggles OpenGL/GLES depending on the target (`BR2_PACKAGE_HAS_LIBGL` vs GLES support).
- **Build system:** CMake release build that disables server builds, staticizes libs, and installs the client binary plus the `quake3` keys under `/usr/share/evmapy`.
