# UQM (Ur-Quan Masters)

Rebuilds the Ur-Quan Masters (Star Control II) engine from source.

## Build notes
- **Version:** commit `d6583f2250e...` from `sc2/uqm`.
- **Config:** requires SDL2, libpng, libvorbis, and libzip. Depends on `BR2_STATIC_LIBS` being disabled because of SDL2.
- **Build system:** CMake release build that produces shared and static libraries, installs the `urquan` binary into `/usr/bin`, and copies `uqm.keys` into `/usr/share/evmapy`.
