# Azahar

Azahar is REG-Linux's modern Citra-based 3DS emulator, combining Qt6 tooling with FFT/SDL media stacks so handheld games work within the distro's frontend.

## Build notes

- `Version`: 2123.3
- `Dependencies`: `BR2_PACKAGE_REGLINUX_QT6`, `BR2_PACKAGE_FMT`, `BR2_PACKAGE_BOOST`, `BR2_PACKAGE_BOOST_SERIALIZATION`, `BR2_PACKAGE_BOOST_IOSTREAMS`, `BR2_PACKAGE_BOOST_REGEX`, `BR2_PACKAGE_BOOST_LOCALE`, `BR2_PACKAGE_BOOST_CONTAINER`, `BR2_PACKAGE_FFMPEG`, `BR2_PACKAGE_SDL2`, `BR2_PACKAGE_FDK_AAC`
- `Build helper`: CMake-based (`cmake-package`)
- `Extras`: installs `3ds.azahar.keys` into `/usr/share/evmapy` (or the equivalent key directory)
