# Sonic 3 A.I.R. (Angel Island Revisited)

The Oxygen Engine-based Sonic 3 A.I.R. port targets REG-Linux with GLSL/GLES variants and the distro’s SDL/ALSA stack.

## Build notes

- `Version`: `v24.02.02.0-stable` from `Eukaryot/sonic3air`.
- `Dependencies`: `BR2_PACKAGE_SDL2`, `BR2_PACKAGE_LIBCURL`, `BR2_PACKAGE_ZLIB`, `BR2_PACKAGE_ALSA_LIB`, optional `BR2_PACKAGE_XORG7`, `BR2_PACKAGE_HAS_LIBGL` or `BR2_PACKAGE_HAS_LIBGLES`.
- `Build helper`: CMake-based (`cmake-package`) using the GLES-specific `CMakeLists.txt.gles2` for `_gles2`.
- `Extras`: deploys `/usr/bin/sonic3-air` plus configs/data/save folders, strips remastered audio for small hosts, and copies `sonic3-air.keys` into `/usr/share/evmapy`.
