# liblcf

`liblcf` is the data library from the EasyRPG project that reads/writes RPG Maker 2000/2003 LCF and XML files. REG-Linux keeps it as a standalone Buildroot package so other components (e.g., the player or libretro core) can link against a staged library.

## Build configuration
- **Version:** 0.8.1 via the EasyRPG GitHub repository.
- **Dependencies (Config):** selects `expat`, `ICU`, and `inih` so the parser can handle XML and legacy INI formats.
- **Build system:** CMake; builds both shared and static variants and requires `LIBLCF_SUPPORTS_IN_SOURCE_BUILD = NO` so tone separate build directory.
- **Staging:** enabled to ensure downstream packages can find the headers/libs (
  `LIBLCF_INSTALL_STAGING = YES`).
