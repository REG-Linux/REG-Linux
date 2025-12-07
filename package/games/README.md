# REG-Linux games

`package/games` gathers self-contained game ports that ship both engines and data within REG-Linux. Each folder defines a Buildroot `Config.in`, its `.mk` recipe with any patches, and supporting assets such as controller key lists or game data packs.

## Contents
- `abuse/` + `abuse-data/`: Xenoveritas' SDL build of Abuse plus the optional data pack.
- `cdogs/`: multiplayer-oriented overhead shooter with Python and ENet bits.
- `hcl/` and `hurrican/`: Hydra Castle Labyrinth and the SDL2-powered Hurrican platformer.
- `lbreakouthd/`, `ltris2/`, `sdlpop/`, `tyrian/`, `warzone2100/`, `sonic3-air/`: modernized arcade/retro ports built via CMake/autotools with custom asset/install hooks.
- `libretro/`: additional libretro cores tailored for games (Mr. Boom, Super Bros War).

Each subdirectory now hosts a README summarizing dependencies, build flow, and any REG-Linux-specific install steps.
