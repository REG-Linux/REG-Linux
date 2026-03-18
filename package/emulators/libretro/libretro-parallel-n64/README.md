# libretro-parallel-n64

Nintendo 64 libretro core (Parallel N64). Upstream: https://github.com/libretro/parallel-n64

Dynarec is selected per-arch (`WITH_DYNAREC=aarch64/arm/x86_64`). Desktop GL disables GLES (`FORCE_GLES=0`); otherwise `FORCE_GLES=1`. Vulkan enables `HAVE_PARALLEL=1` and, on x86_64, `HAVE_PARALLEL_RSP=1`.
