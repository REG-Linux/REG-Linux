# eka2l1

Symbian OS / N-Gage emulator. Upstream: https://github.com/EKA2L1/EKA2L1

Requires Qt6. Selects X11 or Wayland backend via `-DEKA2L1_UNIX_USE_X11/WAYLAND` depending on `BR2_PACKAGE_REGLINUX_XWAYLAND`. GCC 14 incompatible-pointer-types errors suppressed via `CFLAGS`/`CXXFLAGS`. Installs everything to `/usr/eka2l1/`.
