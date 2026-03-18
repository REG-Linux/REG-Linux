# Yamagi Quake II family

Yamagi Quake II client and mission packs. Upstream: https://github.com/yquake2

Each mission pack (`yquake2-xatrix`, `yquake2-rogue`, `yquake2-ctf`, `yquake2-zaero`) installs its `game.so` under `/usr/yquake2/<packname>/` so the base client can load it. SDL3 is preferred when available, with SDL2 as fallback.
