# Azahar

Nintendo 3DS emulator (Citra fork). Upstream: https://github.com/azahar-emu/azahar

Qt6 frontend enabled when `BR2_PACKAGE_REGLINUX_HAS_QT6` is set; otherwise the SDL2 frontend is used. Vulkan requires both `BR2_PACKAGE_XWAYLAND` and `BR2_PACKAGE_REGLINUX_VULKAN`. SSE 4.2 paths enabled only on `x86_64_v3` targets.
