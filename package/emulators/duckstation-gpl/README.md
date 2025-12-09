# DuckStation GPL

DuckStation GPL provides REG-Linux with the upstream-licensed PlayStation 1 emulator, featuring Qt6 tooling plus extensive SIMD and ARM fixes.

## Build notes

- `Version`: v0.1-7294
- `Dependencies`: `BR2_PACKAGE_REGLINUX_QT6`, `BR2_PACKAGE_FMT`, `BR2_PACKAGE_BOOST`, `BR2_PACKAGE_FFMPEG`, `BR2_PACKAGE_SDL2`, `BR2_PACKAGE_WEBP`, `BR2_PACKAGE_LIBEVDEV`, `BR2_PACKAGE_LIBDRM`, `BR2_PACKAGE_LIBCURL`, `BR2_PACKAGE_LUNASVG`, `BR2_PACKAGE_ECM`, `BR2_PACKAGE_LIBXKBCOMMON`, `BR2_PACKAGE_SHADERC`, `BR2_PACKAGE_GLSLANG` (when `BR2_PACKAGE_REGLINUX_VULKAN`), `BR2_PACKAGE_LIBBACKTRACE`, `BR2_PACKAGE_CPUINFO`, `BR2_PACKAGE_SPIRV_CROSS`, `BR2_PACKAGE_LIBSOUNDTOUCH`
- `Build helper`: CMake-based (`cmake-package`)
- `Extras`: installs `psx.duckstation-gpl.keys` into `/usr/share/evmapy` and layers REG-Linux patches (`002-path-getdirectory.patch`, `001-path-program.patch`, `010-rewrite-gcc-compliant-simd-code.patch`, `009-fix-code-generator-aarch32.patch`, `007-fix-conversion-on-arm.patch`, `013-fix-gcc-newrec-aarch64.patch`, `003-path-language.patch`, `006-fix-linux-detection.patch`, `004-adjust-paths.patch`, `014-disable-soundtouch-exception.patch`, `012-fix-gcc-jit-buffer.patch`, `008-fix-sdl-binding.patch`, `005-no-discord.patch`, `011-fix-vixl-aarch32-template-id-not-allowed.patch`)
