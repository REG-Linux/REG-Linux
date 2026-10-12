# mupen64plus-gliden64

GLideN64 graphics plugin for Mupen64Plus. Upstream: https://github.com/gonetz/GLideN64

## Build Configuration

This package uses the Buildroot CMake package infrastructure.
It requires `mupen64plus-core` to be built first.

## Dependencies

### Required

- `zlib` - Compression library
- `libpng` - PNG image support
- `mupen64plus-core` - Core emulator library
- `sdl2` - Window/input handling
- `alsa-lib` - Audio (inherited)

### Optional

- `mesa3d` - Mesa OpenGL drivers
- `libgl` - Desktop OpenGL
- `libgles` - OpenGL ES

## Graphics Features

GLideN64 provides:

- High-level graphics rendering
- Resolution upscaling (2x, 4x, 8x native)
- Texture filtering and enhancement
- Widescreen hacks
- Modern OpenGL features
- Vulkan support (optional)

## Build Options

- `MUPENPLUSAPI=ON` - Build as Mupen64Plus plugin
- `MUPENPLUSAPI_GLIDENUI=OFF` - Disable GLideN64 UI
- `USE_SDL=ON` - Enable SDL support
- `USE_SYSTEM_LIBS=ON` - Use system libraries
- `EGL=ON` - Use EGL (when available)
- `MESA=ON` - Enable Mesa-specific optimizations
- `GL_PROFILE=ON` - Enable OpenGL profiling (debug builds)

## Architecture Optimizations

- **ARM with NEON**: `CRC_NEON=ON`
- **AArch64**: `CRC_ARMV8=ON`

## Installation

The plugin is installed to:

- `/usr/lib/mupen64plus/mupen64plus-video-gliden64.so`
- `/usr/share/mupen64plus/GLideN64.ini`

## Configuration

GLideN64 settings are configured in:

- `/usr/share/mupen64plus/GLideN64.ini`

Settings include:

- Resolution scaling
- Texture filtering
- Anisotropic filtering
- Anti-aliasing
- VSync

## Notes

- This is the recommended video plugin for most games
- Provides the best balance of compatibility and performance
- Requires more GPU resources than other plugins
- Debug builds enable OpenGL profiling
