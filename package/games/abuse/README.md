# Abuse SDL

Packages Xenoveritas' SDL port of *Abuse* with REG-Linux asset hooks.

## Build notes
- **Version:** `v0.9.1` (git commit Oct 27, 2022).
- **Config:** selects SDL2 and SDL2_mixer; requires a C++ toolchain (`BR2_INSTALL_LIBSTDCPP`).
- **Build system:** CMake release build with `ABUSE_SUPPORTS_IN_SOURCE_BUILD = NO` and `-DASSETDIR=/userdata/roms/abuse`.
- **Install:** copies the binary to `/usr/bin/abuse` and drops `abuse.keys` into `/usr/share/evmapy`. Data content is sourced from the dedicated `abuse-data` package rather than bundled.
