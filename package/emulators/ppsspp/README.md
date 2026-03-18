# ppsspp

PSP emulator. Upstream: https://github.com/hrydgard/ppsspp

On x86 targets, `OpenGL_GL_PREFERENCE=GLVND` is forced and `libglew`/`libglu` are added. Vulkan enabled when `BR2_PACKAGE_REGLINUX_VULKAN` is set; `USING_X11_VULKAN` toggled by xwayland presence. On non-xwayland GLES platforms, `EGL_NO_X11` and `MESA_EGL_NO_X11_HEADERS` are defined. mipsel+musl uses system ffmpeg.
