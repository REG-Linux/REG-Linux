# Engine packages for REG-Linux

This directory hosts the custom engine packages that REG-Linux provides to Buildroot. Every subdirectory below corresponds to a `package/` entry with its own `Config.in`, build recipe, and supporting patches or key files.

## Contents
- `easyrpg/`: builds the EasyRPG interpreter plus its data parser library (`liblcf`).
- `ikemen/`: compiles the Go-based Ikemen Mugen engine with GTK/OpenAL/GL bindings and on-target keymaps.
- `libretro/`: provides two libretro cores, `libretro-easyrpg` and `libretro-scummvm`, for frontend integration.
- `lightspark/`: builds the Lightspark Flash runtime with GLES fallbacks.
- `moonlight-embedded/`: the Gamestream client tailored for embedded systems.
- `openbor/`: holds multiple OpenBOR engine revisions (4432, 6330, 6412, 6510, 7142, 7530) each with its own Buildroot package.
- `reglinux-scummvm/`: distributes a REG-Linux prebuilt bundle containing ScummVM and the libretro core plus their evmapy keys.
- `ruffle/`: compiles the Rust-based Ruffle Flash emulator including the desktop binary and evmapy keys.
- `scummvm/`: builds ScummVM from source with the usual SDL2/codec stack and evmapy keys.
- `solarus-engine/`: builds the Solarus Lua-driven engine with custom patches for input handling and dynamic libs.
- `thextech/`: builds the TheXTech SMBX engine with GLES and SDL2 tweaks.
- `vpinball/`: builds Visual Pinball with its CMake plumbing, libbass download step, and additional runtime assets.

Refer to the README inside each subfolder for package-specific notes, patches, and build hooks.
