# ET: Legacy

Open-source recreation of *Wolfenstein: Enemy Territory* using SDL2 and CMake.

## Build notes
- **Version:** v2.83.2 (Jan 2025), built from git with `libtheora`, `libvorbis`, `OpenAL`, SSL, minizip, cJSON, and PNG/SQL dependencies.
- **Config:** selects the full codec stack plus `Lua`, `OpenGL`, `OpenSSL`, and `cJSON`; when `BR2_PACKAGE_REGLINUX_XWAYLAND` is enabled, GL, GLEW, and GLU are required.
- **Build system:** CMake release build with static libs, `BUILD_SERVER=OFF`, `BUILD_MOD=ON`, cross-compilation tricks for Poppler/LuaJIT, explicit renderer selection (GL for non-ARM, GLES otherwise), and no bundled libs.
- **Extras:** installs the main binary and `legacy_2.83-dirty.pk3`, copies the controller keys to `/usr/share/evmapy`, and adds the data file to `/usr/share/etlegacy`.
