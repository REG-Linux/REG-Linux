# ECWolf

Wolfenstein 3D source port. Upstream: https://github.com/ECWolfEngine/ECWolf

Requires a `host-ecwolf` build (`-DTOOLS_ONLY=ON`) to produce `ImportExecutables.cmake` for cross-compilation. Pre-generated `gdtoa` headers (`arith.h`, `gd_qnan.h`) are copied in during post-configure because they cannot be computed on the host for the target. The binary installs to `/usr/share/ecwolf/ecwolf` with a symlink at `/usr/bin/ecwolf`. Adds `musl-fts` on musl toolchains.
