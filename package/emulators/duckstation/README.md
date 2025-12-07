# BR2_PACKAGE_DUCKSTATION

DuckStation - PlayStation 1, aka. PSX Emulator DuckStation features a fully-featured frontend built using Qt.

## Build notes

- ``Version``: v0.1-9669
- ``Config``: depends on BR2_x86_64 || BR2_arm || BR2_aarch64
- ``Build helper``: Generic/Makefile (generic-package)
- ``Extras``: copies `psx.duckstation.keys` into `/usr/share/evmapy` or equivalent
