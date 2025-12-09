# DuckStation

DuckStation is REG-Linux's Qt-backed PlayStation 1 emulator with a polished UI and robust compatibility.

## Build notes

- `Version`: v0.1-9669
- `Dependencies`: `BR2_x86_64` or `BR2_arm` or `BR2_aarch64`
- `Build helper`: Generic/Makefile (`generic-package`)
- `Extras`: copies `psx.duckstation.keys` into `/usr/share/evmapy` (or the equivalent key directory)
