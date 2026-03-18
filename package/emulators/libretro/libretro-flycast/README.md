# libretro-flycast

Dreamcast / Naomi / Atomiswave libretro core (Flycast). Upstream: https://github.com/flyinghead/flycast

Shares the version pin with the standalone flycast package. GL backend is selected per-platform: desktop GL, GLES3, or GLES2 in that priority order. Vulkan is enabled when `BR2_PACKAGE_REGLINUX_VULKAN` is set. Per-SoC flags (`-DRK3399=ON`, `-DRPI4=ON`, `-DS922X=ON`, etc.) tune recompiler behaviour.
