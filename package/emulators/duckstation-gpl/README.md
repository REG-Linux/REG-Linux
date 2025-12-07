# BR2_PACKAGE_DUCKSTATION_GPL

See Buildroot configs for details.

## Build notes

- ``Version``: v0.1-7294
- ``Config``: select BR2_PACKAGE_REGLINUX_QT6, select BR2_PACKAGE_FMT, select BR2_PACKAGE_BOOST, select BR2_PACKAGE_FFMPEG, select BR2_PACKAGE_SDL2, select BR2_PACKAGE_WEBP, select BR2_PACKAGE_LIBEVDEV, select BR2_PACKAGE_LIBDRM, select BR2_PACKAGE_LIBCURL, select BR2_PACKAGE_LUNASVG, select BR2_PACKAGE_ECM, select BR2_PACKAGE_LIBXKBCOMMON, select BR2_PACKAGE_SHADERC, select BR2_PACKAGE_GLSLANG	if BR2_PACKAGE_REGLINUX_VULKAN, select BR2_PACKAGE_LIBBACKTRACE, select BR2_PACKAGE_WEBP, select BR2_PACKAGE_CPUINFO, select BR2_PACKAGE_SPIRV_CROSS, select BR2_PACKAGE_LIBSOUNDTOUCH
- ``Build helper``: CMake-based (cmake-package)
- ``Extras``: copies `psx.duckstation-gpl.keys` into `/usr/share/evmapy` or equivalent; applies patches: 002-path-getdirectory.patch, 001-path-program.patch, 010-rewrite-gcc-compliant-simd-code.patch, 009-fix-code-generator-aarch32.patch, 007-fix-conversion-on-arm.patch, 013-fix-gcc-newrec-aarch64.patch, 003-path-language.patch, 006-fix-linux-detection.patch, 004-adjust-paths.patch, 014-disable-soundtouch-exception.patch, 012-fix-gcc-jit-buffer.patch, 008-fix-sdl-binding.patch, 005-no-discord.patch, 011-fix-vixl-aarch32-template-id-not-allowed.patch
