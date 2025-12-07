# HLSDK Xash3D Opposing Force

Opposing Force-specific Half-Life SDK libs.

## Build notes
- **Branch:** `opforfixed` (commit `0310381f...`).
- **Config:** same SDL2 stack plus libsodium.
- **Build system:** CMake with `-DGOLDSOURCE_SUPPORT=1`, `-DSERVER_LIBRARY_NAME=opfor`, and `-DGAMEDIR=gearbox` to match the mod directory.
- **Install:** drops the `cl_dlls` and `dlls` under `/usr/lib/xash3d/hlsdk/opfor/`.
