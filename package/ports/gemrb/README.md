# GemRB (Infinity Engine clone)

`gemrb` is the reimplementation of the Infinity Engine used by Baldur's Gate, Icewind Dale, and Planescape: Torment.

## Build notes
- **Version:** v0.9.4 (release).
- **Config:** selects SDL2, SDL2_mixer, OpenAL, FreeType, Zlib, ICU, PNG, Vorbis/Ogg, libcurl, and conditionally GL/GLES to match the target.
- **Build system:** CMake release build that forces static linking, disables libVLC, and optionally enables OpenGL/GLES backends depending on the target. Installation strips the binary and removes the demo data; comments remain for future evmapy integration.
