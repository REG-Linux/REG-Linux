# REG-Linux ports

The `package/ports` tree reproduces REG-Linux' collection of PC/console engine ports and rebuilds. Every directory defines a Buildroot `Config.in`, the underlying `.mk` recipe, and supporting assets (patches, keys, helper data). Choose the top-level package to discover its dependencies, build requirements, and any supplemental installs needed for REG-Linux' frontend.

## Highlights
- `libretro/`: additional libretro cores for classic ports (PrBoom, NXEngine, etc.).
- `xash3d/`: Xash3D-FWGS engine plus the Half-Life SDK variants required by its mods.
- `yquake2/`: Yamagi Quake II and the associated mission packs (Xatrix, Rogue, CTF, Zaero) packaged separately.
- `raze`, `gzdoom`, `vcmi`, `ioquake3`, etc.: upstream-minded SDL/CMake builds that bake in REG-Linux evmapy keys and custom init data.

Each subfolder now hosts a README with package-specific notes.
