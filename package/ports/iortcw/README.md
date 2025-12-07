# IORTCW (Return to Castle Wolfenstein)

Builds the IORTCW project with both single-player and multiplayer binaries plus the default REG-Linux config.

## Build notes
- **Version:** commit `438e7d...` (May 2024) that targets both SP/MP builds with `generic-package` + custom Makefiles.
- **Config:** selects SDL2 and OpenAL; the Makefile toggles VOIP, codecs, renderer choices, and OpenGL/GLES features per architecture (x86_64 vs ARM/RISC-V).
- **Install hooks:** installs dedicated directories under `/usr/bin/iortcw`, copies the `wolfconfig.cfg` file under `/usr/share/reglinux/datainit/roms/iortcw/main` to keep fullscreen enabled, and publishes `iortcw.keys` under `/usr/share/evmapy`.
