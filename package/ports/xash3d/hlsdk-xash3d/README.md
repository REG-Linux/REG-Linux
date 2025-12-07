# HLSDK Xash3D (generic)

Builds the Half-Life SDK libraries required by numerous GoldSource mods via the `mobile_hacks` branch.

## Build notes
- **Branch:** `mobile_hacks` on Jan 3, 2025 (Version `c525400a...`).
- **Config:** selects SDL2, SDL2_mixer, SDL2_image, SDL2_ttf, and libsodium.
- **Build system:** uses Waf (`waf-package`) with `--build-type=release` and an optional `--64bits` flag on 64-bit hosts.
- **Install:** deploys the compiled `cl_dlls` and `dlls` into `/usr/lib/xash3d/hlsdk/hl/` so Xash3D-FWGS can find them.
