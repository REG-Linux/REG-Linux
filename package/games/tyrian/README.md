# Tyrian (OpenTyrian)

The `opentyrian` port packages the DOS shmup *Tyrian* with SDL2/SDL2_net so REG-Linux can ship the player-friendly binary.

## Build notes

- `Version`: `v2.1.20221123` from `opentyrian/opentyrian`.
- `Dependencies`: `BR2_PACKAGE_SDL2`, `BR2_PACKAGE_SDL2_NET`, `BR2_INSTALL_LIBSTDCPP`.
- `Build helper`: Generic (`generic-package`) invoking the upstream Makefile with `PREFIX=$(STAGING_DIR)/usr`.
- `Extras`: installs `/usr/bin/opentyrian` and copies `tyrian.keys` into `/usr/share/evmapy`.
