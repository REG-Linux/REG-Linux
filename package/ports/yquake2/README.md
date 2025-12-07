# Yamagi Quake II family

`yquake2` is the central port that gathers the Yamagi Quake II client plus the mission packs (Xatrix, Rogue, CTF, Zaero) as separate packages. All child packages install their shared `game.so` libraries into `/usr/yquake2/` so the base client can load them.

- `yquake2-client/`: main engine; builds GL/GLES renderers, installs multiple renderer modules, and drives the base Quake II binary.
- `yquake2-xatrix/`, `yquake2-rogue/`, `yquake2-ctf/`, `yquake2-zaero/`: each provides a mission pack library (`game.so`).

Refer to the subREADME inside each directory for per-package details (shared dependencies, renderer toggles, install paths).
