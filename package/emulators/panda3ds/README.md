# panda3ds

Nintendo 3DS emulator. Upstream: https://github.com/wheremyfoodat/Panda3DS

Vulkan renderer and `host-glslang` (for shader compilation) added only when `BR2_PACKAGE_REGLINUX_VULKAN` is set. GLX is patched out of the GLAD loader (`002-glad-no-glx.patch`).
