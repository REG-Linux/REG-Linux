# REG-Linux games

`package/games` keeps the self-contained game ports that ship engines and data assets for consoles, PCs, and arcade-inspired homebrew. Every subfolder defines its own `Config.in`, `.mk` recipe, and README that covers versions, dependencies, patches, extras, and any EVMapy key/data hooks.

## Package notes
- `abuse/`: installs the Xenoveritas SDL port of *Abuse*, pointing the asset dir at `/userdata/roms/abuse` so the companion `abuse-data` pack or downloader can supply the data.
- `abuse-data/`: unpacks the 2.00 public-domain archive into `/usr/share/abuse`, offering the original game files to the `abuse` binary.
- `cdogs/`: builds `cdogs-sdl` with SDL2/ENet and Python protobuf support, dropping `cdogs.keys` under `/usr/share/evmapy` and expecting the content downloader to provide the asset tree.
- `hcl/`: compiles Hydra Castle Labyrinth with SDL2, SDL2_mixer, and the distro’s pad patches so the 16-bit platformer runs on consoles.
- `hurrican/`: packages the Hurrican SDL2 shooter with GLES2 rendering, OpenMP, and SDL2_image/epoxy/OpenMPT helpers.
- `lbreakouthd/`: rounds up the SDL2-based Breakout clone via Autotools and the Musl-aware configure patch.
- `ltris2/`: ships the classic Tetris clone with SDL2/mixer/ttf support and cross-build helpers for non-MMU targets.
- `sdlpop/`: delivers the SDLPoP Prince of Persia port, copying the repo’s `data/` folder, configs, and `sdlpop.keys` for controller mapping.
- `sonic3-air/`: installs the Oxygen Engine Sonic 3 A.I.R. port, including GLES2 features and EVMapy controller keys.
- `tyrian/`: brings OpenTyrian to REG-Linux via the upstream Makefile and copies `tyrian.keys` into place for the DOS-era shmup.
- `warzone2100/`: ships the open-source Warzone 2100 RTS with a full CMake build against SDL2, OpenAL, SQLite, PhysFS, protobuf, and libzip.
- `libretro/`: builds game-specific libretro cores (`libretro-mrboom`, `libretro-superbroswar`) so the same engines also load inside RetroArch-style frontends.

For the exact Buildroot wiring, consult each subdirectory’s README and associated `.mk` file.
