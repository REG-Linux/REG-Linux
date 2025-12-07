# VCMI (Heroes of Might and Magic 3 engine)

Open-source reimplementation of Heroes of Might and Magic 3.

## Build notes
- **Version:** 1.6.8 (Jan 2025) built from `vcmi/vcmi` with Git submodules.
- **Config:** selects SDL2, SDL2_image/mixer/ttf, FFmpeg, minizip, TBB, and a broad Boost set; musl adds `libexecinfo`. Qt6 and REG-Linux Qt bindings are optional for the launcher/editor.
- **Build system:** CMake release build with Ninja, static libraries, and toggles for launcher/translations (Qt6 only). The install path is `/usr/vcmi/`.
