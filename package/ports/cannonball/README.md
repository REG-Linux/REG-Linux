# Cannonball (OutRun engine)

Packages the OutRun-inspired `cannonball-se` source tree with REG-Linux-friendly defaults.

## Build notes
- **Version:** commit `aa77386...` (October 2025) with the `sdl2` build target (`sdl2gl` on x86_64, `sdl2gles` elsewhere) and MP3 support toggled based on `BR2_PACKAGE_MPG123`.
- **Config:** selects `SDL2`, `Boost`, and the musl helpers when applicable; also installs controller keys under `/usr/share/evmapy`.
- **Customization:** release build uses `-flto=auto`, disables native codegen, and injects `dataroot`/`config` paths under `/userdata`. The install step places `tilemap.bin`, `tilepatch.bin`, and `config_help.txt` under `/usr/share/reglinux/datainit/system/configs/cannonball/` before copying the `.keys` file.
