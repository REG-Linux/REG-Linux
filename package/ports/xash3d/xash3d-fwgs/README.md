# xash3d-fwgs

Xash3D-FWGS engine with packaging tweaks for REG-Linux.

## Build notes
- **Version:** commit `b5b6dad...` (Jan 2025) from `FWGS/xash3d-fwgs`.
- **Config:** selects SDL2, SDL2_image/mixer/ttf, FreeType, Fontconfig, and the HLSDK packages (DMC/Opposing Force) to cover all mods.
- **Build system:** Waf release build that forces packaging, disables VGUI/menu toggles, and adds `--disable-gl`/`--enable-gl4es` when GLES is the only backend.
- **Extras:** `LIBRETRO` packaging is not triggered; the Waf build itself is the install target, and no extra keys are needed beyond the dep tree.
