# EDuke32 / Fury

Rebuilds the Build Engine port used for Duke Nukem 3D and the standalone *Fury* expansion.

## Build notes
- **Version:** commit `39967d8` (Nov 2025) from the `terminx/eduke32` repo.
- **Config:** selects SDL2, FLAC, libvpx, and optionally `libexecinfo` for musl toolchains; depends on OpenGL/GLES so it requires `BR2_PACKAGE_HAS_LIBGL` or `BR2_PACKAGE_HAS_LIBGLES`.
- **Build system:** custom `Makefile` build invoked via `generic-package` that sets `STARTUP_WINDOW=0`, disables GTK, forces `USE_OPENGL=1`, and builds the `fury` variant (`FURY=1`). Two binaries (`eduke32`/`fury`) end up in `/usr/bin`, and the same `.keys` file is duplicated for both (one for Fury in `/usr/share/evmapy/fury.keys`).
