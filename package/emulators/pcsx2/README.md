# PCSX2

PCSX2 brings PlayStation 2 emulation to REG-Linux with the upstream `v2.4.0` tree plus EVMapy keys, QT6 tooling, and Vulkan support toggles.

## Build notes

- `Version`: v2.4.0
- `Dependencies`: `BR2_PACKAGE_FMT`, `BR2_PACKAGE_JPEG_TURBO`, `BR2_PACKAGE_WEBP`, `BR2_PACKAGE_ALSA_LIB`, `BR2_PACKAGE_FREETYPE`, `BR2_PACKAGE_ZLIB`, `BR2_PACKAGE_LIBPNG`, `BR2_PACKAGE_LIBAIO`, `BR2_PACKAGE_PORTAUDIO`, `BR2_PACKAGE_LIBSOUNDTOUCH`, `BR2_PACKAGE_LIBSAMPLERATE`, `BR2_PACKAGE_SDL3`, `BR2_PACKAGE_DEJAVU`, `BR2_PACKAGE_LIBPCAP`, `BR2_PACKAGE_YAML_CPP`, `BR2_PACKAGE_VULKAN_HEADERS`, `BR2_PACKAGE_VULKAN_LOADER` (when `BR2_PACKAGE_REGLINUX_VULKAN`), `BR2_PACKAGE_REGLINUX_QT6`, `BR2_PACKAGE_SHADERC`, `BR2_PACKAGE_ECM`, `BR2_PACKAGE_LIBBACKTRACE`, `BR2_PACKAGE_KDDOCKWIDGETS`, `BR2_PACKAGE_PLUTOSVG`, `BR2_x86_64`, `BR2_PACKAGE_XORG7`
- `Build helper`: CMake-based (`cmake-package`)
- `Extras`: copies `ps2.pcsx2.keys` into `/usr/share/evmapy` and applies REG-Linux patches (`009-fix-cmake-pure-wayland.patch`, `001-fix-Savestates-path.patch`, `006-patches-in-bios-folder.patch`, `004-controller-db.patch`, `000-fix-linux-compilation-always_inline.patch`, `007-fix-sdl-input.patch`, `005-lightguns.patch`, `008-fix-cmake-link.patch`, `003-fix-linux-detection.patch`, `002-fix-linux-compilation-headers-gs.patch`)
