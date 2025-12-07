# BR2_PACKAGE_PCSX2

PCSX2 is a free and open-source PlayStation 2 (PS2) emulator. https://github.com/PCSX2/pcsx2

## Build notes

- ``Version``: v2.4.0
- ``Config``: select BR2_PACKAGE_FMT, select BR2_PACKAGE_JPEG_TURBO, select BR2_PACKAGE_WEBP, select BR2_PACKAGE_ALSA_LIB, select BR2_PACKAGE_FREETYPE, select BR2_PACKAGE_ZLIB, select BR2_PACKAGE_LIBPNG, select BR2_PACKAGE_LIBAIO, select BR2_PACKAGE_PORTAUDIO, select BR2_PACKAGE_LIBSOUNDTOUCH, select BR2_PACKAGE_LIBSAMPLERATE, select BR2_PACKAGE_SDL3, select BR2_PACKAGE_DEJAVU, select BR2_PACKAGE_LIBPCAP, select BR2_PACKAGE_YAML_CPP, select BR2_PACKAGE_VULKAN_HEADERS    if BR2_PACKAGE_REGLINUX_VULKAN, select BR2_PACKAGE_VULKAN_LOADER     if BR2_PACKAGE_REGLINUX_VULKAN, select BR2_PACKAGE_REGLINUX_QT6, select BR2_PACKAGE_SHADERC, select BR2_PACKAGE_ECM, select BR2_PACKAGE_LIBBACKTRACE, select BR2_PACKAGE_KDDOCKWIDGETS, select BR2_PACKAGE_PLUTOSVG, depends on BR2_x86_64, depends on BR2_PACKAGE_XORG7
- ``Build helper``: CMake-based (cmake-package)
- ``Extras``: copies `ps2.pcsx2.keys` into `/usr/share/evmapy` or equivalent; applies patches: 009-fix-cmake-pure-wayland.patch, 001-fix-Savestates-path.patch, 006-patches-in-bios-folder.patch, 004-controller-db.patch, 000-fix-linux-compilation-always_inline.patch, 007-fix-sdl-input.patch, 005-lightguns.patch, 008-fix-cmake-link.patch, 003-fix-linux-detection.patch, 002-fix-linux-compilation-headers-gs.patch
