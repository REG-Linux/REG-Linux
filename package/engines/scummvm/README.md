# ScummVM

Builds ScummVM v2.9.1 from source with the codec stack and UI tweaks used by REG-Linux.

## Configuration
- **Build selects:** SDL2, libmpeg2, libjpeg(+BATO), libogg/vorbis (or Tremor on ARM/MIPS), FLAC, libmad, libpng, libtheora, FAAD2, freetype, zlib, and codecs required by `BR2_PACKAGE_HAS_SCUMMVM`.
- **Build options:** configures OpenGL/GLES per target, enables plugins/dynamic builds on non-x86_64 targets, toggles Tremor versus Vorbis, and enables NEON/SSE/AVX2 extensions where appropriate. Munt/fluid synthesizer support is conditional on the toolchain having those packages.
- **Patches:** `001-screenshotsdir.patch` (adjusts screenshot directory) and `002-rpi-sdl2.patch` (targets Raspberry Pi SDL2 configuration).
- **Extras:** installs virtual keyboard packs and copies `scummvm.keys` to `/usr/share/evmapy` via `SCUMMVM_ADD_VIRTUAL_KEYBOARD`.
