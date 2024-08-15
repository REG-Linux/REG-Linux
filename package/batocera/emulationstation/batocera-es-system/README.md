## Directory navigation

 - `batocera-es-system.py` The Python script which generates `es_features.cfg` and `es_systems.cfg` based on the `es_features.yml` and `es_systems.yml` YML files.
 - `es_systems.yml` The systems that ES recognizes and shows on the system list when the user has installed the appropriate ROMs. Contains some metadata about the system, such as full name and manufacture date. This is the file you'd want to edit if you want to put a comment in the generated roms/<system>/_info.txt file.
 - `es_features.yml` The configuration file EmulationStation uses to show which options are available for each system (in “features”). Also includes the advanced per-system settings (in “cfeatures” as their own unique entries). Used in conjunction with the [config generators](https://github.com/batocera-linux/batocera.linux/tree/master/package/batocera/core/batocera-configgen/configgen/configgen/generators) to define new options. The user may override this with a custom file.
 - `roms` Batocera's pre-bundled ROMs, and other necessary files for the ROMs directory. Follow the links to know more and support their authors.

    | &#9000; | ***Atari 2600*** |  |  |
    | :---: | :---: | :--- | :--- |
    | &#9734; | ![Amoeba Jump](https://raw.githubusercontent.com/REG-Linux/REG-Linux/master/package/batocera/emulationstation/batocera-es-system/roms/atari2600/images/Amoeba-Jump-marquee.png) | Author: Dionoid | https://atariage.com/forums/topic/280211-amoeba-jump/ |
    |  |  |  |  |
    | &#9000; | ***Commodore 64*** |  |  |
    | &#9734; | ![Relentless 64](https://raw.githubusercontent.com/REG-Linux/REG-Linux/master/package/batocera/emulationstation/batocera-es-system/roms/c64/images/Relentless64-marquee.png) | Authors: Paul 'Axelay' Kooistra; Harris 'rexbeng' Kladis; Pierre 'Cyborgjeff' Martin | https://rgcddev.itch.io/relentless-64 |
    | &#9733; | ![Showdown](https://raw.githubusercontent.com/REG-Linux/REG-Linux/master/package/batocera/emulationstation/batocera-es-system/roms/c64/images/Showdown-marquee.png) | Author: Henning Ludvigsen | https://www.badgerpunch.com/title/showdown/ |
    |  |  |  |  |
    | &#9000; | ***Game Boy Advance*** |  |  |
    | &#9733; | ![Anguna - Warriors of Virtue](https://raw.githubusercontent.com/REG-Linux/REG-Linux/master/package/batocera/emulationstation/batocera-es-system/roms/gba/images/Anguna-marquee.png) | Author: Bite The Chili | http://www.tolberts.net/anguna/ |
    |  |  |  |  |
    | &#9000; | ***Game Boy Color*** |  |  |
    | &#9734; | ![Petris](https://raw.githubusercontent.com/REG-Linux/REG-Linux/master/package/batocera/emulationstation/batocera-es-system/roms/gbc/images/Petris-marquee.png) | Author: bbbbbr | https://bbbbbr.itch.io/petris |
    |  |  |  |  |
    | &#9000; | ***Master System*** |  |  |
    | &#9734; | ![Mai Nurse](https://raw.githubusercontent.com/REG-Linux/REG-Linux/master/package/batocera/emulationstation/batocera-es-system/roms/mastersystem/images/Mai-Nurse-marquee.png) | Author: lunoka | https://lunoka.itch.io/mai-nurse |
    |  |  |  |  |
    | &#9000; | ***Mega Drive / Genesis*** |  |  |
    | &#9733; | ![Hayato's Journey](https://raw.githubusercontent.com/REG-Linux/REG-Linux/master/package/batocera/emulationstation/batocera-es-system/roms/megadrive/images/Hayato-Journey-marquee.png) | Author: Master Linkuei | https://master-linkuei.itch.io/hayatos-journey |
    | &#9734; | ![Old Towers](https://raw.githubusercontent.com/REG-Linux/REG-Linux/master/package/batocera/emulationstation/batocera-es-system/roms/megadrive/images/Old-Towers-marquee.png) | Author: Denis Grachev | https://retrosouls.itch.io/old-towers |
    |  |  |  |  |
    | &#9000; | ***Nintendo Entertainment System*** |  |  |
    | &#9734; | ![Alter Ego](https://raw.githubusercontent.com/REG-Linux/REG-Linux/master/package/batocera/emulationstation/batocera-es-system/roms/nes/images/Alter-Ego-marquee.png) | Author: Shiru | https://shiru.untergrund.net/ |
    |  |  |  |  |
    | &#9000; | ***Super Nintendo Entertainment System*** |  |  |
    | &#9733; | ![Dottie Flowers](https://raw.githubusercontent.com/REG-Linux/REG-Linux/master/package/batocera/emulationstation/batocera-es-system/roms/snes/images/Dottie-Flowers-marquee.png) | Author: Goldlocke | https://goldlocke.itch.io/dottie-flowers |
    | &#9734; | ![Super Boss Gaiden](https://raw.githubusercontent.com/REG-Linux/REG-Linux/master/package/batocera/emulationstation/batocera-es-system/roms/snes/images/Super-Boss-Gaiden-marquee.png) | Authors: Dieter von Laser; Chrono Moogle | https://superbossgaiden.superfamicom.org/ |
    |  |  |  |  |
    | &#9000; | ***PC Engine*** |  |  |
    | &#9733; | ![Dinoforce](https://raw.githubusercontent.com/REG-Linux/REG-Linux/master/package/batocera/emulationstation/batocera-es-system/roms/pcengine/images/Dinoforce-marquee.png) | Author: PCE Works | https://dinoforce.pceworks.net/ |
    |  |  |  |  |
    | &#9000; | ***Ports*** |  |  |
    | &#9734; | ![DOOM (shareware)](https://raw.githubusercontent.com/REG-Linux/REG-Linux/master/package/batocera/emulationstation/batocera-es-system/roms/prboom/images/doom1_shareware-marquee.png) | Author: id Software | https://prboom.sourceforge.net/ |
    | &#9734; | ![MrBoom](https://raw.githubusercontent.com/REG-Linux/REG-Linux/master/package/batocera/emulationstation/batocera-es-system/roms/mrboom/images/MrBoom-marquee.png) | Author: Remdy Software | https://github.com/Javanaise/mrboom-libretro |
    | &#9733; | ![OD Commander](https://raw.githubusercontent.com/REG-Linux/REG-Linux/master/package/batocera/emulationstation/batocera-es-system/roms/odcommander/images/od-commander-marquee.png) | Author: glebm | https://github.com/od-contrib/commander |
    | &#9734; | ![SDLPoP](https://raw.githubusercontent.com/REG-Linux/REG-Linux/master/package/batocera/emulationstation/batocera-es-system/roms/sdlpop/images/sdlpop-marquee.png) | Author: NagyD | https://github.com/NagyD/SDLPoP |
