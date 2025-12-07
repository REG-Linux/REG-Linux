# OpenLara

Open-source Tomb Raider 1 engine that compiles cross-platform depending on GL vs GLES.

## Build notes
- **Version:** commit `7a80d8f3...` (November 2025).
- **Config:** pulls in `Zlib`, `OpenAL`, and `SDL2`.
- **Build system:** custom manual build (invokes `clang++`/`gcc` via `$(TARGET_CXX)` and `sdl2-config`) that selects GL+desktop libs on x86_64 or GLES2/GLES3 on GPUs lacking GL.
- **Install:** copies the resulting `OpenLara` binary to `/usr/bin`.
