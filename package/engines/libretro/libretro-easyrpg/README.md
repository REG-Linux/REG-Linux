# libretro-easyrpg

EasyRPG Player built as a libretro core. Upstream: https://github.com/EasyRPG/Player

Configured with `-DPLAYER_TARGET_PLATFORM=libretro` and requires `liblcf` staged in the sysroot. Optional `harfbuzz` and `fluidsynth` are pulled in when their Buildroot counterparts are enabled. The resulting `easyrpg_libretro.so` installs under `/usr/lib/libretro/`.
