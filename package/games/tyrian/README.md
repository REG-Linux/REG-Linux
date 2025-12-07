# Tyrian (OpenTyrian)

Open-source port of the DOS shmup *Tyrian*.

## Build notes
- **Version:** `v2.1.20221123` from `opentyrian/opentyrian`.
- **Config:** selects SDL2 and SDL2_net.
- **Build system:** custom Makefile build invoked via `generic-package` using `PREFIX=$(STAGING_DIR)/usr` and cross-toolchain flags so the resulting binary links against the staged SDL2 libs.
- **Install extras:** installs `opentyrian` under `/usr/bin` and copies `tyrian.keys` into `/usr/share/evmapy`.
