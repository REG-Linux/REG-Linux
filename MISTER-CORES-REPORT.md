# MiSTer FPGA Cores vs REG-Linux Systems Report

Generated: 2026-02-19

## Legend

| Status | Meaning |
|--------|---------|
| **Excellent** | Production-ready, actively maintained, high compatibility |
| **Good** | Production-ready, stable, minor limitations |
| **Beta** | Playable but known issues, may be under active development |
| **WIP** | Work in progress, limited compatibility |
| **None** | No MiSTer core exists for this system |

---

## Currently Mapped Systems (in system_map.rs + es_systems.yml)

### Console Cores

| REG-Linux System | MiSTer Core | Core Quality | Save States | Notes |
|---|---|---|---|---|
| `nes` | NES_MiSTer | **Excellent** | Yes (mapper-dependent) | FDS, expansion audio, NSF player. Excellent compatibility |
| `snes` | SNES_MiSTer | **Excellent** | Experimental | SA-1, SuperFX, DSP, SDD1, CX4, MSU-1 all supported. Satellaview + SPC player |
| `megadrive` | Genesis_MiSTer | **Excellent** | No | SVP (Virtua Racing) supported. Being superseded by MegaDrive (Nuked-MD) |
| `segacd` | MegaCD_MiSTer | **Excellent** | No | Requires BIOS. CHD + BIN/CUE supported. No 32X combo |
| `sega32x` | S32X_MiSTer | **Beta** | No | Sound pitch issues in some games. No Mega CD+32X combo. Region detection issues |
| `mastersystem` | SMS_MiSTer | **Excellent** | No | FM audio, lightgun, paddle. Shares core with Game Gear and SG-1000 |
| `gamegear` | SMS_MiSTer | **Excellent** | No | Same core as SMS. Some video setting differences |
| `sg1000` | SG1000 variant | **Good** | No | Handled by SMS core in some builds, dedicated in others |
| `psx` | PSX_MiSTer | **Excellent** | Yes | Very feature-rich. Requires SDRAM + 3 regional BIOS files |
| `saturn` | Saturn_MiSTer | **Beta** | No | ~95% US library playable. SCSP audio accurate. Active development (srg320) |
| `pcengine` | TurboGrafx16_MiSTer | **Excellent** | No | SuperGrafx, CD-ROM, Arcade Card. Mouse + multitap support |
| `pcenginecd` | TurboGrafx16_MiSTer | **Excellent** | No | Same core as pcengine. CD+G only in CloneCD format |
| `supergrafx` | SuperGrafx variant | **Good** | No | Part of TurboGrafx16 core or dedicated |
| `neogeo` | NeoGeo_MiSTer | **Excellent** | No | AES + MVS. 128MB SDRAM needed for ~15% of library. Encrypted ROMs not supported |
| `atari2600` | Atari2600 variant | **Good** | No | Part of Atari7800 core which also handles 2600. Most bankswitching supported |
| `atari7800` | Atari7800_MiSTer | **Good** | No | ARM-based mappers (DPC+) NOT supported (impossible on Cyclone V) |
| `colecovision` | ColecoVision_MiSTer | **Good** | No | Keypad input via overlay. BIOS required |
| `intellivision` | Intv_MiSTer | **Beta** | No | Only 8 directions vs original 16. ECS + Intellivoice supported. Multiple BIOS needed |
| `vectrex` | Vectrex_MiSTer | **Good** | No | Vector display emulation. Small but complete library |
| `o2em` | Odyssey2_MiSTer | **Good** | No | Magnavox Odyssey 2 / Philips Videopac |
| `channelf` | ChannelF_MiSTer | **Good** | No | First programmable cartridge console. Very niche |
| `astrocde` | Astrocade_MiSTer | **Good** | No | Bally Astrocade. Requires boot ROM. Niche library |

### Handheld Cores

| REG-Linux System | MiSTer Core | Core Quality | Save States | Notes |
|---|---|---|---|---|
| `gb` | Gameboy_MiSTer | **Excellent** | Yes | Excellent accuracy. Link cable via 2P core |
| `gbc` | Gameboy_MiSTer | **Excellent** | Yes | Same core as GB |
| `gba` | GBA_MiSTer | **Excellent** | Yes | Cycle-accurate. BIOS recommended. 32MB+ SDRAM |
| `gameandwatch` | GameNWatch_MiSTer | **Good** | No | Individual G&W simulations |
| `lynx` | Lynx_MiSTer | **Excellent** | Yes | All official games playable. Requires boot ROM + 64MB SDRAM |
| `wswan` | WonderSwan_MiSTer | **Good** | No | All WS variants. Requires 2 BIOS + SDRAM |
| `wswanc` | WonderSwan_MiSTer | **Good** | No | Same core as wswan |
| `supervision` | Supervision_MiSTer | **Good** | No | Watara SuperVision. Very niche |
| `gamate` | Gamate_MiSTer | **Good** | No | Bit Corporation Gamate. Very niche |
| `megaduck` | MegaDuck variant | **Good** | No | Mega Duck / Cougar Boy |
| `advision` | AdventureVision variant | **Good** | No | Entex Adventure Vision. Very niche |

### Computer Cores

| REG-Linux System | MiSTer Core | Core Quality | Save States | Notes |
|---|---|---|---|---|
| `c64` | C64_MiSTer | **Excellent** | No | Dual 1541 drives. Excellent SID emulation |
| `amiga` | Minimig-AGA_MiSTer | **Excellent** | No | OCS/ECS/AGA. 500/600/1200/4000/CD32/CDTV. WHDLoad supported |
| `amiga500` | Minimig-AGA_MiSTer | **Excellent** | No | Same core as amiga, OCS/ECS mode |
| `amiga1200` | Minimig-AGA_MiSTer | **Excellent** | No | Same core as amiga, AGA mode |
| `msx` | MSX_MiSTer | **Excellent** | No | MSX / MSX2 / MSX2+ / turbo R |
| `msx1` | MSX_MiSTer | **Excellent** | No | Same core as msx |
| `msx2` | MSX_MiSTer | **Excellent** | No | Same core as msx |
| `dos` | AO486_MiSTer | **Good** | No | 486DX-33, no hardware FPU. SB Pro/16 + OPL. Can run Win 3.1/95/98 |

---

## MiSTer Cores NOT Yet Mapped in REG-Linux

These MiSTer cores exist and are production-quality but don't have a REG-Linux system mapping yet.

### High Priority (popular systems, quality cores)

| MiSTer Core | System | Quality | REG-Linux System Name | Recommendation |
|---|---|---|---|---|
| N64_MiSTer | Nintendo 64 | **Good** | `n64` | **ADD** - ~99% library playable. No save states. Dev ended but stable |
| MegaDrive_MiSTer | Mega Drive (Nuked-MD) | **Excellent** | `megadrive` | **UPDATE** - cycle-accurate decap-based core, successor to Genesis |
| SGB_MiSTer | Super Game Boy | **Good** | `sgb` | **ADD** - Plays GB games with SNES borders/palettes |
| Gameboy2P_MiSTer | Game Boy 2-Player | **Good** | — | SKIP - niche (needs 2 SDRAM sticks) |
| GBA2P_MiSTer | GBA 2-Player | **Good** | — | SKIP - niche (needs 2 SDRAM sticks) |
| PokemonMini_MiSTer | Pokemon Mini | **Good** | `pokemini` | **ADD** - small but complete library |

### Medium Priority (less popular but quality cores)

| MiSTer Core | System | Quality | REG-Linux System Name | Recommendation |
|---|---|---|---|---|
| Atari800_MiSTer | Atari 5200 / 800XL | **Good** | `atari5200` / `atari800` | **ADD** - shares core, both computer and console |
| AtariST_MiSTer | Atari ST/STe | **Beta** | `atarist` | **ADD** - known issues but usable |
| ZX-Spectrum_MiSTer | ZX Spectrum | **Excellent** | `zxspectrum` | **ADD** - excellent compatibility |
| Amstrad_MiSTer | Amstrad CPC | **Excellent** | `amstradcpc` | **ADD** - excellent compatibility |
| BBCMicro_MiSTer | BBC Micro | **Good** | `bbcmicro` | ADD - well-regarded UK computer |
| Apple-II_MiSTer | Apple IIe | **Good** | `apple2` | ADD - missing floppy write but good |
| VIC20_MiSTer | Commodore VIC-20 | **Good** | `vic20` | ADD - good compatibility |
| C16_MiSTer | Commodore C16/Plus4 | **Good** | `c16` | ADD - TED chip emulation |
| PCXT_MiSTer | IBM PC/XT | **Good** | `pcxt` | ADD - 8088, CGA/MDA/Tandy |
| TI-99_4A_MiSTer | TI-99/4A | **Good** | `ti99` | ADD - speech synth supported |
| CoCo3_MiSTer | Tandy CoCo 3 | **Good** | `coco` | ADD - enhanced CoCo |

### Low Priority (very niche or limited cores)

| MiSTer Core | System | Quality | Recommendation |
|---|---|---|---|
| Jaguar_MiSTer | Atari Jaguar | **WIP/Beta** | WAIT - not yet in MiSTer-devel, still improving |
| X68000_MiSTer | Sharp X68000 | **Beta** | WAIT - significant graphics problems |
| PC88_MiSTer | NEC PC-8801 | **Beta** | ADD if Japan audience needed |
| MacPlus_MiSTer | Macintosh Plus | **Good** | ADD - niche but works well |
| Archie_MiSTer | Acorn Archimedes | **Good** | ADD - niche UK computer |
| CreatiVision_MiSTer | VTech CreatiVision | **Good** | SKIP - extremely niche |
| VC4000_MiSTer | Interton VC4000 | **Good** | SKIP - extremely niche |
| Arcadia_MiSTer | Emerson Arcadia 2001 | **Good** | SKIP - extremely niche |

---

## Systems in REG-Linux with Concerns

These systems are currently mapped but may need attention:

| REG-Linux System | Issue | Recommendation |
|---|---|---|
| `saturn` | **Beta** quality — ~95% US library but framebuffer limited, some crashes | **KEEP** but note beta status. Active development |
| `sega32x` | **Beta** — sound issues, no MCD+32X | **KEEP** with caveats. Most games work |
| `intellivision` | **Beta** — only 8/16 directions, garbled graphics in some transitions | **KEEP** but lower priority. Playable |
| `advision` | Very niche (~20 games exist). Core quality unknown | KEEP but lowest priority |
| `megaduck` | Very niche handheld. Tiny library | KEEP but lowest priority |
| `supervision` | Very niche. Watara SuperVision | KEEP but lowest priority |
| `gamate` | Very niche. Bit Corporation handheld | KEEP but lowest priority |

---

## Summary: Cores by Tier

### Tier 1 - Excellent (flagship MiSTer experience)
`nes`, `snes`, `megadrive`, `segacd`, `mastersystem`, `gamegear`, `psx`, `pcengine`, `pcenginecd`, `neogeo`, `gb`, `gbc`, `gba`, `lynx`, `c64`, `amiga`/`amiga500`/`amiga1200`, `msx`/`msx1`/`msx2`

### Tier 2 - Good (solid experience)
`atari2600`, `atari7800`, `colecovision`, `vectrex`, `o2em`, `channelf`, `astrocde`, `wswan`, `wswanc`, `supergrafx`, `gameandwatch`, `dos`, `sg1000`

### Tier 3 - Beta / Limited
`saturn` (rapidly improving), `sega32x` (sound issues), `intellivision` (direction limitation)

### Tier 4 - Very Niche (tiny libraries)
`advision`, `megaduck`, `supervision`, `gamate`

---

## Arcade Cores

MiSTer has **hundreds** of individual arcade cores covering Capcom (CPS-1/2/3), SNK, Sega (System 1/16/18), Taito, Konami, Irem, Data East, Namco, Atari, Williams, Midway, Cave, and many more. These require per-game MRA files and specific ROM formats (MAME-derived). Arcade core support could be added as a future phase but requires a different architecture (per-game core loading rather than per-system).

---

## Missing System Mapping: Quick Reference

Systems with **quality MiSTer cores** that should be added to `system_map.rs`:

```
("n64",           "N64"),           // Nintendo 64 - ~99% compatible
("sgb",           "SGB"),           // Super Game Boy
("pokemini",      "PokemonMini"),   // Pokemon Mini
("atari5200",     "Atari800"),      // Atari 5200 (shared core)
("atari800",      "Atari800"),      // Atari 800/XL/XE
("atarist",       "AtariST"),       // Atari ST/STe (beta)
("zxspectrum",    "Spectrum"),      // ZX Spectrum
("amstradcpc",    "Amstrad"),       // Amstrad CPC
("apple2",        "Apple-II"),      // Apple IIe
("vic20",         "VIC20"),         // Commodore VIC-20
("bbcmicro",      "BBCMicro"),      // BBC Micro
("ti99",          "TI-99_4A"),      // TI-99/4A
("coco",          "CoCo3"),         // Tandy Color Computer
("pcxt",          "PCXT"),          // IBM PC/XT
```
