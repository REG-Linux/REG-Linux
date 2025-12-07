# TheForceEngine (Dark Forces)

Modernized Jedi engine that supports Dark Forces and mods.

## Build notes
- **Version:** v1.22.420 release with the `df_patch4` extra content.
- **Config:** selects SDL2, SDL2_image, GL/libs, and optionally RtMidi when available; musl toolchains add `libexecinfo`.
- **Build system:** CMake release build that enables the script engine, downloads the patch zip into `reglinux/datainit`, and copies the `theforceengine.keys` into `/usr/share/evmapy`.
- **Extras:** copies documentation assets, fonts, shaders, soundfonts, and mods into `/usr/share/reglinux/datainit/system/configs/theforceengine/` during install.
