# Xash3D-FWGS tree

This folder keeps the Xash3D-FWGS engine alongside the Half-Life SDK helper libraries required by various GoldSource mods.

## Contents
- `hlsdk-xash3d/`: general Half-Life SDK libs built from the `mobile_hacks` branch.
- `hlsdk-xash3d-dmc/`: Deathmatch Classic-specific SDK.
- `hlsdk-xash3d-opfor/`: Opposing Force-specific SDK.
- `xash3d-fwgs/`: the actual Xash3D-FWGS engine that links against the above SDK packages and toggles GLES/GL.

Each package documents its version, branches, and install targets.
