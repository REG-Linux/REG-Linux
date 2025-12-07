# dhewm3 (Doom 3)

Cross-compiles the GPL Doom 3 port built with SDL2.

## Build notes
- **Version:** 1.5.4, built from the `dhewm/dhewm3` git tree with `neo` subdir as the build target.
- **Config:** selects SDL2, libjpeg, libogg/vorbis, OpenAL, libcurl, and zlib; the package builds host tools by virtue of the `host-dhewm3` dependency.
- **Build system:** CMake release build that disables tests, uses static libs, and copies the `doom3.dhewm3.keys` file into `/usr/share/evmapy` via `post-install`.
