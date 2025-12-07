# BR2_PACKAGE_86BOX

86Box https://86box.net/

## Build notes

- ``Version``: v5.2
- ``Config``: select BR2_PACKAGE_RTMIDI, select BR2_PACKAGE_LIBSNDFILE, select BR2_PACKAGE_SLIRP, select BR2_PACKAGE_OPENAL, select BR2_PACKAGE_SDL2
- ``Build helper``: CMake-based (cmake-package)
- ``Extras``: applies patches: 002-reglinux-fix-build.patch, 001-reglinux-vulkan-optional.patch
