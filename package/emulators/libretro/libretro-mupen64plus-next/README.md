# libretro-mupen64plus-next

Nintendo 64 libretro core (Mupen64Plus Next). Upstream: https://github.com/libretro/mupen64plus-libretro-nx

x86_64 builds enable `HAVE_PARALLEL_RSP=1 HAVE_PARALLEL_RDP=1 HAVE_THR_AL=1 LLE=1`; GLES targets pass `FORCE_GLES3=1` or `FORCE_GLES=1` with `GL_LIB=-lGLESv2`; EGL-only platforms add `-DEGL_NO_X11`. Requires `host-nasm`.
