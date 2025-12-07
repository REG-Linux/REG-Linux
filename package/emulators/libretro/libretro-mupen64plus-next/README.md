# BR2_PACKAGE_LIBRETRO_MUPEN64PLUS_NEXT

See Buildroot configs for details.

## Build notes

- ``Version``: 1b693cdac7c42979f6ef53ffe260a76454f0cf45
- ``Config``: depends on (BR2_PACKAGE_HAS_LIBGLES  && !BR2_PACKAGE_SYSTEM_TARGET_X86_64_ANY) || \
- ``Build helper``: Generic/Makefile (generic-package)
- ``Extras``: applies patches: 003-makefile-add-sm8250.patch, 002-RPi5-tuning.patch, 005-makefile-arm64-fix.patch, 004-makefile-adjust-rpi-targets.patch, 001-gcc-fix.patch, 000-makefile.patch
