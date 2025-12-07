# CorsixTH (Theme Hospital)

CorsixTH reimplements Theme Hospital for modern systems with Lua scripting and SDL2.

## Build notes
- **Version:** v0.69.1 release from `CorsixTH/CorsixTH`.
- **Config:** selects Lua, Luafilesystem, LuaSocket, LuaSec, SDL2, SDL2_image, SDL2_mixer, FFmpeg, and libcurl for networking/media.
- **Build system:** straight CMake release build; installs the binary via `cmake-package` and copies `corsixth.keys` into `/usr/share/evmapy` during post-install.
