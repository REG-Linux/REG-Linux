# dxx-rebirth (Descent 1 & 2)

`dxx-rebirth` cross-compiles the Descent source ports with SCons.

## Build notes
- **Version:** commit `b58db2d...` (Nov 2025) from `dxx-rebirth/dxx-rebirth`.
- **Config:** selects SDL2, SDL2_{image,mixer}, PhysFS, LibPNG, and optionally libGL/GLES depending on the host; requires `host-scons` to drive the build.
- **Build system:** uses `host-scons` with `opengl`/`opengles` toggles, passes through toolchain flags, and installs the two binaries (`d1x-rebirth` and `d2x-rebirth`).
- **Extras:** copies `dxx-rebirth.keys` into `/usr/share/evmapy` during post-install.
