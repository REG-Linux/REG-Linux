# OpenJazz

Free/open-source Jazz Jackrabbit games.

## Build notes
- **Version:** 20240919 release from `AlisterT/openjazz`.
- **Config:** selects `SDL2` and depends on a C++ toolchain.
- **Build system:** standard CMake release build; installs `OpenJazz` into `/usr/bin`.
- **Extras:** copies the `openjazz.keys` file to `/usr/share/evmapy` and the `openjazz.cfg` template into `/usr/share/reglinux/datainit/system/configs/` for REG-Linux data init.
