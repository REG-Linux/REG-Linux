# Engine packages for REG-Linux

The `package/engines` tree collects REG-Linux’s curated game engines, interpreters, and streaming helpers that ship alongside the emulator stack. Each subfolder defines its own `Config.in`, `.mk` recipe, and supporting assets (patches, keys, helper files) tailored to the distro’s GPUs, input stack, and frontend requirements.

## Engine summaries
- `easyrpg/`: Builds the EasyRPG interpreter plus `liblcf`, exposing RPG Maker 2000/2003 games with SDL2 audio/video and the distro’s input stack.
- `ikemen/`: Compiles the Go-powered Ikemen Mugen engine with GTK/OpenAL bindings and REG-Linux control mappings so bespoke fighting game collections run out of the box.
- `libretro/`: Hosts dedicated libretro cores for EasyRPG and ScummVM, letting the same engines surface through RetroArch-style frontends.
- `lightspark/`: Packages the Lightspark Flash runtime, complete with GLES fallbacks and runtime patches that replace deprecated GLX behavior.
- `moonlight-embedded/`: Produces the Gamestream client tailored for embedded hardware, compiling the network stack and optional VDPAU/OpenGL backends.
- `openbor/`: Keeps several OpenBOR revisions (4432/6330/6412/6510/7142/7530) in sync, each with its own README, patches, and branch-specific config.
- `reglinux-scummvm/`: Delivers REG-Linux’s bundled ScummVM release plus the libretro core, EVMapy key bundles, and any post-install helper scripts.
- `ruffle/`: Builds the Rust-based Ruffle Flash emulator, including desktop binaries, SDL helpers, and the external key/assets roll referenced by the distro.
- `scummvm/`: Compiles ScummVM from source with the standard SDL2/codec/compatibility stack and copies the required evmapy keys into `/usr/share/evmapy`.
- `solarus-engine/`: Ports the Lua-driven Solarus engine with REG-Linux patches for input handling, dynamic libs, and Qt/SDL integrations.
- `thextech/`: Manages TheXTech (Sega SMBX) engine builds, enabling GLES/SDL2 tweaks and sprite patching so the homebrew platform runs on console hardware.
- `vpinball/`: Builds the Visual Pinball runtime with its CMake plumbing, libbass download step, and extra runtime assets that keep pinball tables working.

Each README in the list explains the package’s version, dependencies, build helper (CMake/Autotools/Generic), and any additional assets/patches that accompany the engine. Refer to the subdirectory README for its detailed build notes.
