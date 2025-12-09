# Ryujinx

Ryujinx runs Nintendo Switch titles on REG-Linux, covering x86_64 and ARM hosts with GL/Vulkan toggles.

## Build notes

- `Version`: 1.3.3
- `Dependencies`: `BR2_x86_64 || BR2_aarch64`, `BR2_PACKAGE_HAS_LIBGL || BR2_PACKAGE_REGLINUX_VULKAN`
- `Build helper`: Generic/Makefile (`generic-package`)
- `Extras`: copies `switch.ryujinx.keys` into `/usr/share/evmapy`
