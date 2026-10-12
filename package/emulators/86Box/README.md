# 86Box

PC hardware emulator. Upstream: https://github.com/86Box/86Box

Qt6 frontend is enabled when `BR2_PACKAGE_REGLINUX_HAS_QT6` is set, otherwise headless. Dynarec is arch-specific: `NEW_DYNAREC=ON` for ARM/AArch64, `DYNAREC=ON` for x86_64, off elsewhere. FluidSynth MIDI is optional.
