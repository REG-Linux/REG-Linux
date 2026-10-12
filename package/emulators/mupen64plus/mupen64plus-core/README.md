# mupen64plus-core

Core module of the Mupen64Plus project. Upstream: https://github.com/mupen64plus/mupen64plus-core

## Build Configuration

This package uses the Buildroot generic-package infrastructure with custom build commands.
The build targets the `projects/unix` subdirectory.

## Dependencies

### Required

- `sdl2` - Input and window management
- `alsa-lib` - Audio output
- `freetype` - Font rendering
- `dejavu` - Font files
- `host-nasm` - Assembler for x86 code

### Optional

- `libglu` - OpenGL Utility Library (if using desktop OpenGL)
- `vulkan-headers` / `vulkan-loader` - Vulkan support (when `BR2_PACKAGE_REGLINUX_VULKAN=y`)

## Architecture Support

- **ARMv7**: Uses VFP hard-float and NEON optimizations
- **ARMv8 (AArch64)**: Uses NEON optimizations
- **x86_64**: Uses SSE optimizations
- **RISC-V 64**: Supported without SIMD optimizations

## Configuration

The following parameters are set based on architecture:

- `HOST_CPU` - Target CPU architecture
- `VFP_HARD=1` - VFP hard-float for ARM
- `NEON=1` - NEON SIMD for ARM with NEON
- `USE_GLES=1` - Use OpenGL ES instead of desktop OpenGL
- `VULKAN=1` - Enable Vulkan support (optional)

## Patches

This package includes several REG-Linux specific patches:

- **000-start-message.patch**: Hides "Mupen64Plus Started..." OSD message
- **001-allow-96MB.patch**: Increases RDRAM size limit to 96MB
- **002-mupeninifile.patch**: Custom INI file handling
- **003-statenameasromfilename.patch**: Uses ROM filename for savestates
- **004-statesasromname.patch**: Savestate naming improvements
- **005-fix-gcc14.patch**: Fixes GCC 14 compatibility issues

## Installation

The core library is installed to:

- `/usr/lib/libmupen64plus.so.2.0.0`
- `/usr/share/mupen64plus/mupen64plus.ini`
- `/usr/share/mupen64plus/mupencheat.txt`
- `/usr/share/mupen64plus/font.ttf` (symlink to DejaVu Sans)

## Notes

- This package exports `MUPEN64PLUS_GL_CFLAGS`, `MUPEN64PLUS_GL_LDLIBS`, and `MUPEN64PLUS_PARAMS` for use by other mupen64plus packages
- The build uses custom Makefile targets rather than standard CMake or autotools
