# HLSDK Xash3D DMC (Deathmatch Classic)

Deathmatch Classic-specific SDK libraries for Xash3D.

## Build notes
- **Branch:** `dmc` branch snapshot `2eaaf125...` (Jan 2025).
- **Config:** same SDL2/SDL2_mixer/image/ttf + libsodium stack.
- **Build system:** CMake with `-DGOLDSOURCE_SUPPORT=1`, updates the server library name to `dmc`, and flags `DGAMEDIR=dmc`.
- **Install:** copies the generated `cl_dll` and `dll` libs into `/usr/lib/xash3d/hlsdk/dmc/`.
