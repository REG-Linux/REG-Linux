# OpenBOR 6330

`openbor6330` builds DCurrent's `v6330` branch with the SDL2 + libvpx stack tuned for modern targets.

## Configuration
- **Config selection:** selects `libvpx`, `SDL2`, `SDL2_gfx`, `libpng`, `libogg`, and `libvorbis`.
- **Version:** tagged `v6330` from the `DCurrent/openbor` GitHub repo.
- **Build flow:** runs `engine/version.sh` to pick the release string and drives `make` inside `engine/` with `BUILD_LINUX` or `BUILD_ARM` depending on the target. Installs `OpenBOR6330` to `/usr/bin`.

## Included patches
- `0001-Fix-anim_list-and-model_cache-definitions.patch`
- `001-x86_64.patch`
- `002-fixkeys.patch`
- `003-arm.patch`
- `004-warnings.patch`
- `005-axismanagement.patch`
- `006-fix-pad-axis-combos-player-running.patch`
- `998-openbor-c.patch`
- `998-openbor-h.patch`
- `999-openbor-h.patch`
