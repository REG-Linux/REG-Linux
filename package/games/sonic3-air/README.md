# Sonic 3 A.I.R. (Angel Island Revisited)

Ports the Oxygen Engine version of Sonic 3 for Linux.

## Build notes
- **Version:** `v24.02.02.0-stable` from `Eukaryot/sonic3air`.
- **Config:** requires SDL2, libcurl, zlib, optional GL or GLES support, ALSA, and X11 libs when `BR2_PACKAGE_XORG7` is enabled. Builds only when GL or GLES is available.
- **Build system:** CMake release build with a GLES-specific `CMakeLists.txt.gles2` (copied into `_gles2` during pre-configure) and the normal Oxygen/sonic3air subtree for Xorg.
- **Install:** copies the executable, configs, data, scripts, and save folders into `/usr/bin/sonic3-air`, removes remastered audio to save space on constrained targets, and installs `sonic3-air.keys` under `/usr/share/evmapy`.
