# DOSBox-X

DOSBox-X extends classic DOSBox with more compatibility and a Windows-style configuration dialog; REG-Linux keeps the Autotools build streamlined to match its packaging targets.

## Build notes

- `Version`: dosbox-x-v2025.12.01
- `Dependencies`: `BR2_PACKAGE_SDL2`, `BR2_PACKAGE_SDL2_NET`, `BR2_PACKAGE_ZLIB`, `BR2_PACKAGE_LIBPNG`, `BR2_PACKAGE_LIBOGG`, `BR2_PACKAGE_LIBVORBIS`, `BR2_INSTALL_LIBSTDCPP`
- `Build helper`: Autotools (`autotools-package`)
- `Extras`: copies `dos.dosbox-x.keys` into `/usr/share/evmapy` (or the equivalent key directory) and applies REG-Linux patches (`004-aarch64-MT32.patch`, `001-sdl-config.patch`, `003-dosboxconf.patch`, `002-map_mouse.patch`, `000-arm_configure.patch`)
