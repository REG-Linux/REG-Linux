# Commander Genius

Commander Keen engine reimplementation. Upstream: https://github.com/gerstrong/Commander-Genius

The Cosmos engine is a git submodule of Commander Genius (`src/engine/cosmos`, Dringgstein/cosmos `testing` branch) and comes in with the release it is pinned to (`CGENIUS_GIT_SUBMODULES`); it is compiled with `-DBUILD_COSMOS=1`. CMake >= 3.29 is required, so Buildroot builds its own host-cmake. Adds `libbacktrace`/`libexecinfo` on musl.

Controller input is pad-to-keyboard: CG binds joysticks only by raw per-pad `Joy<n>-B<button>` indices, so regmsgd's evmapy port drives it instead, from `regmsg/lua/generators/keys/cgenius.json`. The matching player-1 keyboard bindings are pinned into `[input0]` of `cgenius.cfg` by `cgenius.lua` — the two have to agree, so change them together. (This package installed a `cgenius.keys` for the standalone evmapy daemon once; that file and that daemon are both gone.)
