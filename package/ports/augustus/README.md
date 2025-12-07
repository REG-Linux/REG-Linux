# Augustus (Caesar 3 enhancements)

`augustus` builds the Keriew project that modernizes *Caesar III* with the Julius UI features.

## Build notes
- **Version:** latest commit as of November 2025 (`1bacfa9...`).
- **Config:** selects `SDL2`, `SDL2_mixer`, and `libpng`; adds `libbacktrace`/`libexecinfo` when the toolchain uses musl.
- **Build system:** CMake release build that disables shared libraries and builds out-of-tree (`cmake-package`).
- **Extras:** none beyond the standard install; the  `README` keeps the version and patch info in sync with the upstream `LICENSE`.
