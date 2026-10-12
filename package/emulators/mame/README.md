# mame

GroovyMAME arcade emulator. Upstream: https://github.com/antonioginer/GroovyMAME

Uses the upstream GNU Makefile directly (not cmake). Always built with `NO_X11=1 USE_WAYLAND=1`. OpenGL disabled when `BR2_PACKAGE_HAS_LIBGL` is unset. PulseAudio optional; ALSA is the fallback. Per-arch `PLATFORM=` and `FORCE_DRC_C_BACKEND=1` for RISC-V. Job count capped at 32 to limit RAM usage.
