# BR2_PACKAGE_TSUGARU

FM TOWNS Emulator "Tsugaru"

## Build notes

- ``Version``: v20250513
- ``Config``: select BR2_PACKAGE_LIBGLU
- ``Build helper``: CMake-based (cmake-package)
- ``Extras``: copies `fmtowns.keys` into `/usr/share/evmapy` or equivalent; applies patches: 001-cmake-fixes.patch
