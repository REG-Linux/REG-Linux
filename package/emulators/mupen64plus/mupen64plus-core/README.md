# mupen64plus-core

Nintendo 64 emulator core (Mupen64Plus). Upstream: https://github.com/mupen64plus/mupen64plus-core

GL flags (`MUPEN64PLUS_GL_CFLAGS`/`MUPEN64PLUS_GL_LDLIBS`) and `USE_GLES=1` are set centrally in this package and inherited by all other plugins. Vulkan support requires `BR2_PACKAGE_REGLINUX_VULKAN`. ARM NEON builds pass `VFP_HARD=1`, NEON CFLAGS, and vectorization flags.
