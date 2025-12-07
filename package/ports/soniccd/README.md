# Sonic CD 2011

Port of the Sonic CD decompilation for Android/iOS/Steam.

## Build notes
- **Version:** 1.3.3 release from `RSDKModding/RSDKv3-Decompilation`.
- **Config:** selects SDL2, SDL2_net/mixer, libogg, libvorbis, libtheora, and GL libs when available.
- **Build system:** Makefile release build that installs the binary as `/usr/bin/soniccd` and copies `sonicretro.soniccd.keys` to `/usr/share/evmapy`.
