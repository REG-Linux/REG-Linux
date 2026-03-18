# Cemu

Wii U emulator. Upstream: https://github.com/cemu-project/Cemu

Vulkan enabled when `BR2_PACKAGE_REGLINUX_VULKAN` is set, OpenGL when desktop GL is present, Wayland when `BR2_PACKAGE_WAYLAND` is set. ARM builds add `-flax-vector-conversions`. `host-pugixml` is required alongside the target pugixml for cross-compilation.
