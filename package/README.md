# REG-Linux packages

The `package/` tree houses every Buildroot recipe REG-Linux maintains—from standalone emulators to ports, firmware helpers, and custom tooling. Each folder is self-contained: it defines a `Config.in`, the `.mk` recipe, and any supporting patches, keys, or assets needed at build time.

## Highlights
- `package/emulators/`: emulator targets (standalone builds and libretro cores) with README summaries that cover versions, dependencies, build helpers, and extra assets.
- `package/ports/`: PC/console engine ports where each entry documents its dependencies and install quirks.
- `package/system/`, `package/core/`, and `package/utils/`: infrastructure packages that glue together the REG-Linux runtime.

Refer to a subdirectory’s README to understand its specific configuration, then follow the `Config.in`/`.mk` pair for the exact Buildroot wiring.
