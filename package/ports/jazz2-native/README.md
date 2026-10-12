# Jazz2 Native

Jazz Jackrabbit 2 engine reimplementation. Upstream: https://github.com/deathkiller/jazz2-native

Forces the nCine SDL2 backend on every target (GLES is added where Xorg + desktop GL are
absent). nCine maps joysticks itself from `SDL_GAMECONTROLLERCONFIG`, but applies that mapping to
the button order its backend reports: GLFW numbers by ascending evdev code, SDL follows joydev
order (0x120+ gamepad range first, stray codes last). Any pad carrying a stray code -- the Retroid
Pocket's `BTN_BACK` -- shifts every button by one under GLFW, so A lands on a dead code and the
d-pad rotates. GLFW additionally enumerates touchscreens as gamepads, where an untouched panel
reads as a stick held hard over.

On OdroidC5 with Mali GPU, `-lmali` is injected into the linker flags. `NCINE_DOWNLOAD_DEPENDENCIES=OFF` prevents in-build fetches.

`001-reglinux-paths.patch` pins the three paths the engine derives from XDG to REG-Linux locations --
the original game files to `/userdata/roms/jazz2/`, the converted cache to
`/userdata/system/cache/jazz2/`, the config to `$XDG_CONFIG_HOME/jazz2` -- and adds `--source <dir>`
and `--cache <dir>` to override the first two at launch.

The overrides exist because the engine only ever scans one directory of original game files, so a
release shipping its own `Anims.j2a` -- Christmas Chronicles, another game version, a mod with its
own tilesets -- cannot be merged into the base one. The regmsg `jazz2` generator uses them to point
the engine at a subfolder of `roms/jazz2` named by a `.game` shortcut, the same convention as
`openjazz`. `--cache` travels with `--source` because the cache is converted from the source and its
validity is keyed only on `Anims.j2a`'s timestamp, which two data sets can easily share.

The libretro core in `package/ports/libretro/libretro-jazz2-native` keeps its own copy of the path
patch; it takes its directories from the RetroArch frontend instead.
