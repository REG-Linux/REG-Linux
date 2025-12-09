# Libretro Mupen64Plus Next

The `libretro-mupen64plus-next` core runs the modern Mupen64Plus backend inside REG-Linux, using GLES support for non-x86_64 targets plus the distro’s ARM Makefile fixes.

## Build notes

- `Version`: 1b693cdac7c42979f6ef53ffe260a76454f0cf45
- `Dependencies`: `(BR2_PACKAGE_HAS_LIBGLES && !BR2_PACKAGE_SYSTEM_TARGET_X86_64_ANY)` (per Config)
- `Build helper`: Generic/Makefile (`generic-package`)
- `Extras`: applies REG-Linux patches (`003-makefile-add-sm8250.patch`, `002-RPi5-tuning.patch`, `005-makefile-arm64-fix.patch`, `004-makefile-adjust-rpi-targets.patch`, `001-gcc-fix.patch`, `000-makefile.patch`)
