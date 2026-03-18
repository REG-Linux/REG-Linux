# flycast

Sega Dreamcast, Naomi, and Atomiswave emulator. Upstream: https://github.com/flyinghead/flycast

GL backend is chosen by arch: desktop GL on x86_64, GLES3 on GLES3 platforms, GLES2 otherwise. Vulkan enabled when `BR2_PACKAGE_REGLINUX_VULKAN` is set. musl disables breakpad. Per-SoC flags for RK3399, RK3568, RPi4/5, SM8250, OdroidXU4, S922X.
