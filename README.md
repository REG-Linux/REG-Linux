## :video_game::penguin: REG Linux :video_game::penguin:
REG Linux is an open-source Retro Emulation Gaming Linux system.
It is a friendly [batocera.linux](https://batocera.org) fork maintaining compatiblity with it, aiming at be lighter and faster, especially on SBCs (ARM 32-bit / AArch64 / RISC-V 64bit) and handdeld devices.

[![Activity](https://img.shields.io/github/commit-activity/m/REG-Linux/REG-Linux)](https://github.com/REG-Linux/REG-Linux)
[![PR](https://img.shields.io/github/issues-pr-closed/REG-Linux/REG-Linux)](https://github.com/REG-Linux/REG-Linux)
[![Stars](https://img.shields.io/github/stars/REG-Linux?style=social)](https://github.com/REG-Linux/REG-Linux)
[![Forks](https://img.shields.io/github/forks/REG-Linux/REG-Linux?style=social)](https://github.com/REG-Linux/REG-Linux)
[![Website](https://img.shields.io/website?down_color=red&down_message=down&up_color=green&up_message=up&url=https%3A%2F%2Fwww.reglinux.org)](https://www.reglinux.org)
[![Discord Server](https://img.shields.io/discord/357518249883205632.svg)](https://discord.gg/fRuETpyg)\
[![Reddit](https://img.shields.io/reddit/subreddit-subscribers/batocera?style=social)](https://www.reddit.com/r/batocera/)
[![Twitter](https://img.shields.io/twitter/follow/REG_linux?style=social)](https://twitter.com/REG_linux)
[![Youtube](https://img.shields.io/youtube/channel/views/UClFpqHKoXsOIV-GjyZqoZcw?style=social)](https://www.youtube.com/channel/UClFpqHKoXsOIV-GjyZqoZcw/featured)

Batocera Linux is an open-source and completely free retro-gaming distribution that can be copied to a USB stick or an SD card with the aim of turning any computer/nano computer into a gaming console during a game or permanently. Batocera Linux does not require any modification on your computer. It supports [many emulators and game engines](https://www.batocera.org/compatibility.php) out of the box. 

## Get information on the project

 - :globe_with_meridians: Browse our [website](https://batocera.org/) for general information and get access to all the latest downloads
 - :memo: Documentation is available on our [wiki](https://wiki.batocera.org/doku.php) and frequently updated
 - :speech_balloon: Discuss any topic with the community on our [Discord Server](https://discord.gg/ndyUKA5)

## Do you need help with Batocera?

 - :sos: The most effective way is to join our [Discord Server](https://discord.gg/ndyUKA5) and go to the \#help-and-support channel
 - :neckbeard: There is a [Batocera subreddit](https://www.reddit.com/r/batocera/) that is fairly active

## How can you help Batocera?

 - :wrench: If you want to help with development, [we accept PRs](https://makeapullrequest.com/)
 - :art: No need to be a developer, you can also [help with translations](https://wiki.batocera.org/help_with_translation), talk about our project on [Youtube](https://www.youtube.com/channel/UClFpqHKoXsOIV-GjyZqoZcw/featured) or [Twitter](https://twitter.com/REG_linux/), create [themes for EmulationStation](https://wiki.batocera.org/themes)
 - :dollar: If you like Batocera, you can help us with a [Paypal donation](), it's always appreciated!
 - :bowtie: Finally, you can now proudly rock some offcial [T-shirts, hoodies and other merch]().

## Directory navigation

 - `board` Platform-specific build configuration. This is where to include special patches/configuration files needed to have particular components work on a particular platform. It is instead encouraged to apply patches at the location of the package itself, but this may not always be possible.
 - `buildroot` Buildroot, the tool used to create the final compiled images. For newcomers, you can safely ignore this folder. Compilation instructions can be found [on the wiki](https://wiki.batocera.org/compile_batocera.linux).
 - `configs` Build flags, which define what components will be built with your image depending on your chose architecture. If you're trying to port Batocera to a new architecture (device, platform, new bit mode, etc.) this is the file you'll need to edit. More information on [the build configuration section on the buildroot compiling page](https://wiki.batocera.org/batocera.linux_buildroot_modifications#define_your_configuration).
 - `package` The "meat and potatoes" of Batocera. This is where the majority of emulator data, config generators, core packages, system utilities, etc. all go into. This is the friendliest place to start dev-work for new devs, as most of it is handled by Python and Makefile.
 - `scripts` Various miscellanous scripts that handle aspects external to Batocera, such as the report data sent to the [compatibility page](https://batocera.org/compatibility.php) or info about the Bezel Project.

A cheatsheet of notable files/folders can be found [on the wiki](https://wiki.batocera.org/notable_files).
