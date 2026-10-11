# libretro-mame

MAME arcade libretro core. Upstream: https://github.com/libretro/mame

Build jobs are capped at 32 to limit RAM usage. A `prepare.py` script (invoked via `host-python3`) strips unwanted drivers before compilation. PulseAudio is disabled with `NO_USE_PULSEAUDIO=1` when not present.
