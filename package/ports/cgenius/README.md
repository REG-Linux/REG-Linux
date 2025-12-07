# Commander Genius (Commander Keen engine)

`cgenius` builds the Commander Keen reimplementation plus the extra Cosmos episode.

## Build notes
- **Version:** v3.6.1 from the `gerstrong/Commander-Genius` repo.
- **Config:** selects `SDL2`, `SDL2_{image,mixer,ttf}`, `Boost`, `xxd`, `python3-configobj`, and musl helpers.
- **Build system:** CMake release build; enables the optional `COSMOS` game module by cloning the `Dringgstein/cosmos` repo during `post-extract`.
- **Extras:** copies `cgenius.keys` into `/usr/share/evmapy` so REG-Linux controller maps are available.
