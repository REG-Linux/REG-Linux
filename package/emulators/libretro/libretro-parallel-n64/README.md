# libretro-parallel-n64

Nintendo 64 libretro core (Parallel N64). Upstream: https://github.com/libretro/parallel-n64

Dynarec is selected per-arch (`WITH_DYNAREC=aarch64/arm/x86_64`); x86_64 needs `host-nasm` for the Ari64 and Hacktarux dynarecs. Desktop GL disables GLES (`FORCE_GLES=0`); otherwise `FORCE_GLES=1 GLES3=1`, since GLideN64 (the default plugin) needs GLES 3.x. Vulkan enables `HAVE_PARALLEL=1` and, on x86_64, `HAVE_PARALLEL_RSP=1`.

Patches:
- `0001` adds the `rpi5_64` platform (BCM2712: aarch64 dynarec, Vulkan only).
- `0002` re-applies upstream's `fsqrt` rename (e38394c3c3), lost in the `device/` tree move; without it the x86_64 Hacktarux dynarec clashes with glibc's C23 `fsqrt()`.
- `0003` lets the `GLES3=1` path build GLideN64 against GLES-only Mesa (no `GL/` headers): bundled `glcorearb.h` fallback plus the one `EXT` typedef it misses.
