# vice

Commodore 8-bit emulator suite. Upstream: https://vice-emu.sourceforge.io/

Builds all Commodore targets (x64, x64sc, x128, xvic, xplus4, xpet, xcbm2, x64dtv, xscpu64) in one recipe. Each target binary is individually selectable via `Config.in`; the post-install hook strips unselected binaries. Requires `host-xa` (6502 assembler) and `host-dos2unix` at build time.
