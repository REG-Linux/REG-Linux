# box64

x86_64 userspace emulator for non-x86 hosts. Upstream: https://github.com/ptitseb/box64

Per-SoC CMake flags are selected at build time: dedicated presets exist for RPi3/4/5, RK3326/3399/3588, OdroidN2, Asahi (M1), SDM845, SM8250/8550, and RV64; everything else falls back to the generic `ARM64` or `RV64` preset.
