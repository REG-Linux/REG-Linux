# Sonic 2013

Port of the Android/iOS Sonic 1 & 2 decompilation using SDL2.

## Build notes
- **Version:** 1.3.3 release from `RSDKModding/RSDKv4-Decompilation`.
- **Config:** selects SDL2, SDL2_net/mixer, libogg/vorbis, and optional GL libs when `BR2_PACKAGE_HAS_LIBGL` is enabled.
- **Build system:** Makefile-driven release build that forces static output, disables the editor, and installs the stripped `sonic2013` binary under `/usr/bin` while copying the `sonicretro.sonic2013.keys` to `/usr/share/evmapy`.
