# Coin Drop Sounds

The Coin Drop Sounds helper adds audible coin-drop feedback to the libretro MAME cores, picking randomly from three training clips and logging extra info when `-verbose` is enabled.

## Build notes

- `Purpose`: injects extra MAME sound assets (`sounder` fallback on Windows) so REG-Linux feels like a full coinbox.
- `Notes`: tested on Windows and Batocera Linux; sound playback uses cuavas’ Reddit tweaks and DKChorus-derived code (Jon Wilson); optional Windows `sounder` package linked at https://download.elifulkerson.com/files/sounder/
