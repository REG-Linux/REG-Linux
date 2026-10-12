# GZDoom

Doom source port (ZDoom). Upstream: https://github.com/ZDoom/gzdoom

Requires a `host-gzdoom` build (`-DTOOLS_ONLY=ON`) to produce `ImportExecutables.cmake` for cross-compilation. Falls back to GLES2 when desktop GL is unavailable. Vulkan is enabled only when both `vulkan-headers`/`vulkan-loader` and a Wayland compositor (Sway or Weston) are present. On musl, `libbacktrace`, `musl-fts`, and LZMA/affinity defines are needed. PK3 files and soundfonts install to `/usr/share/gzdoom/`.
