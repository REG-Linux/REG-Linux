# libretro-ppsspp

PlayStation Portable libretro core (PPSSPP). Upstream: https://github.com/hrydgard/ppsspp

Shares the version pin with the standalone ppsspp package. System ffmpeg is used on mipsel and musl targets (`-DUSE_SYSTEM_FFMPEG=ON`). Vulkan requires `BR2_PACKAGE_REGLINUX_VULKAN`; `USING_X11_VULKAN` is enabled only with xwayland, otherwise `-DEGL_NO_X11=1 -DMESA_EGL_NO_X11_HEADERS=1` are injected.
