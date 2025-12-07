# BR2_PACKAGE_DUCKSTATION_MINI

DuckStation - PlayStation 1, aka. PSX Emulator DuckStation Mini is only for ARM/AArch64 devices. It features a fullscreen/TV UI based on Dear ImGui.

## Build notes

- ``Version``: v0.1-9669
- ``Config``: select BR2_PACKAGE_GMP, depends on BR2_arm || BR2_aarch64, depends on BR2_PACKAGE_HAS_GLES3 || BR2_PACKAGE_REGLINUX_VULKAN
- ``Build helper``: Generic/Makefile (generic-package)
- ``Extras``: copies `psx.duckstation.keys` into `/usr/share/evmapy` or equivalent
