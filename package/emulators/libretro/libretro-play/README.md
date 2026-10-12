# libretro-play

PlayStation 2 libretro core (Play!). Upstream: https://github.com/jpd002/Play-

Uses desktop GL + `libglew` + `libglu` when available; falls back to GLES with `-DUSE_GLEW=OFF -DUSE_GLES=ON`. AArch64 and ARM pass `-DTARGET_PLATFORM_UNIX_AARCH64=YES` / `-DTARGET_PLATFORM_UNIX_ARM=YES`.
