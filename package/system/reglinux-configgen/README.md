# reglinux-configgen

Python-based game and emulator launcher. Upstream: https://github.com/REG-Linux/REG-Linux

The source lives in-tree under `configgen/`. At install time the recipe selects a per-SoC `configgen-defaults-<arch>.yml` from `configs/` and copies it as `configgen-defaults-arch.yml` so each target gets board-specific defaults without touching shared code. On x86_64 a `tdp_hooks.sh` script is added for TDP management; on the CHA target a patch forces CHA controller port 1 detection in the libretro generator. `emulatorlauncher.py` is symlinked to `/usr/bin/emulatorlauncher`.
