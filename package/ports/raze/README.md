# Raze

Build Engine front-end (Duke Nukem 3D, Blood, Shadow Warrior). Upstream: https://github.com/coelckers/Raze

Requires a `host-raze` build to produce `ImportExecutables.cmake`; note that `TOOLS_ONLY=ON` is set but not yet implemented upstream so the host build compiles the full engine. Vulkan is enabled via Wayland when `vulkan-headers`/`vulkan-loader` are present. Falls back to GLES2 when no desktop GL is available. On musl, `libbacktrace`, `musl-fts`, and LZMA/affinity defines are needed.
