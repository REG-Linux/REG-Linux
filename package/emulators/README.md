# REG-Linux emulator packages

This directory collects the Buildroot emulator recipes that REG-Linux builds for classic systems, consoles, and PC hardware. Each subfolder (e.g., `dolphin-emu`, `pcsx2`, `mupen64plus`) defines a `Config.in`, the `.mk` recipe, and supporting assets such as patches, helper keys, or default configs. Every individual package now includes a `README.md` that highlights the selected dependencies, version, build helper, and any post-install assets.

## Categories
- **Retro/console stacks:** `duckstation*`, `pcsx2`, `ppsspp`, `mupen64plus`, `ryujinx`, `rpcs3`, `dolphin-emu`, `dolphin-triforce`, and `mednafen` target dedicated home console hardware.
- **Arcade/PC ports:** `warzone2100`, `tyrian`, `cannonball`, `mame`, `supermodel`, `openmsx`, `sugarbox`, `felix86`, `dosbox-*`, `86Box`, `openmsx`, `bigpemu`, `hypseus-singe`, `snes9x`, `sugarbox`, etc.
- **ARM/embedded:** `box86`, `box64`, `play`, `sugarbox`, `tsugaru`, `sugarbox` (Sega games) show the focus on lighter builds.
- **Libretro cores:** the `libretro/` subtree bundles dozens of retro cores; its README describes the pattern and each core folder now has a dedicated summary.

Browse the individual README under a subdirectory to learn the dependencies, build system (CMake/Autotools/Generic), version, and special install hooks for that emulator.
