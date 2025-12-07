# Sonic Mania

Sonic Mania decompilation port built with SDL2 + PortAudio audio backend.

## Build notes
- **Version:** v1.1.1 release from `RSDKModding/Sonic-Mania-Decompilation`.
- **Config:** selects SDL2, PortAudio (ALSA backend), libogg, and libtheora; adds GL/GLFW/GLU when Xorg+GL is present.
- **Build system:** CMake release build that bundles the `sonic-mania` executable under `/usr/bin`, enables static linking, and copies `sonic-mania.keys` into `/usr/share/evmapy`.
