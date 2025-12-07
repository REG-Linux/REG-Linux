# Visual Pinball

This package builds Visual Pinball (`v10.8.0-2051-28dd6c3`) with a customized CMake flow that normalizes line endings and downloads the BASS audio library on demand.

## Configuration
- **Config selections:** requires `libfreeimage`, `libpinmame`, `libaltsound`, `libdmdutil`, `libdof`, SDL2 (+image/ttf), FFmpeg, and `host-dos2unix` to normalize the codebase.
- **Build flow:** copies the appropriate `CMakeLists_gl-linux-*.txt` file (ARM or x86_64), rewrites include/lib paths to point to `/usr/include` and `/usr/lib`, and downloads the BASS24 zip to stage `libbass.so`.
- **CMake options:** builds Release, disables shared libs, and prevents copying extra runtime libraries.
- **Install:** strips the binary, installs `VPinballX_GL` as `/usr/bin/vpinball`, and copies the `flexdmd`, `assets`, `scripts`, and shader folders into `/usr/bin/vpinball` before copying `vpinball.keys` into `/usr/share/evmapy`.
