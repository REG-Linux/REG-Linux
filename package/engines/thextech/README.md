# TheXTech

TheXTech is a SMBX-compatible platformer engine written in C++.

## Configuration
- **Build system:** CMake with `THEXTECH_CONF_OPTS` enabling SDL2 integration (`USE_SYSTEM_SDL2=ON`), TTF support, and release optimizations.
- **Dependencies:** selects SDL2, SDL2_mixer, and SDL2_ttf via Config and adds them to the `cmake-package` recipe.
- **GL support:** disables modern/legacy desktop GL builds when only GLES is available and toggles GLES2/GLES3 flags accordingly.

## Patches & assets
- `001-fix-gles-builds.patch`, `002-fix-gles-mistakes.patch`, `003-3rdparty-libopus-disable-arm32-asm.patch`, and `004-fix-riscv-detection.patch` ensure the build runs cleanly on embedded hardware.
- During install, copies `thextech.keys` into `/usr/share/evmapy` so the REG-Linux front-end picks up controller maps.
