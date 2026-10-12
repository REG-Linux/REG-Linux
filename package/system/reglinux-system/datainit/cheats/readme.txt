REG Linux -- cheat files
========================

This directory is for .cht files: the libretro cheat format, read by both
RetroArch and REG-Station's built-in player.

Not every cheat is a .cht file
------------------------------

Some emulators carry their own, older cheat collections in their own
formats.  Those do NOT go here.  Each emulator loads its own, from its own
directory, and shows them in its own menu:

  FinalBurn Neo     <setname>.ini  ->  /userdata/bios/fbneo/cheats/
                    Listed under Core Options, not under Cheats.

  MAME              <setname>.xml  ->  /userdata/bios/mame/cheat/
                    Both the standalone and the libretro MAME read this one.
                    Listed in MAME's own menu, opened with TAB.

  MAME 2003-Plus    cheat.dat      ->  /userdata/bios/mame2003-plus/
                    One combined database file, not one file per game.

A .ini or .xml dropped into a folder here will never be read -- not by
RetroArch, not by REG-Station.  Everything below is about .cht files.

Layout
------

    /userdata/cheats/<CORE NAME>/<rom name>.cht

<CORE NAME> is the name the libretro core reports for itself.  The exact
strings are listed at the end of this file.  They are case- and
space-sensitive -- "MAME 2003-Plus" is found, "mame2003-plus" is not.

<rom name> is the ROM's file name with its extension replaced by .cht:

    roms/mame/sf2ce.zip        ->  cheats/MAME/sf2ce.cht
    roms/fbneo/mslugx.zip      ->  cheats/FinalBurn Neo/mslugx.cht
    roms/snes/Sparkster.sfc    ->  cheats/Snes9x/Sparkster.cht

Cheat files downloaded from the libretro cheat database are already sorted
into folders named this way, so they can usually be copied in as they are.
Check the folder names against the list below first -- packs made for older
core versions sometimes use an old name (a FinalBurn pack may say
"FB Alpha", for instance).

Which cheats are switched on
----------------------------

A .cht file records the cheats and, for each one, whether it is on.  Both
frontends read and write that same file, so a cheat you switch on in one is
on in the other -- there is no second copy anywhere to get out of step.

RetroArch rewrites it whenever it saves the SRAM.  REG-Station rewrites it
when you close the in-game cheat menu (Quick Menu -> Cheats) and when you
quit the game.

Neither of them looks anywhere else, so a file has to be in the core folder
to be found at all -- a stray .cht sitting loose in /userdata/cheats is
ignored by both.

Are the two compatible?
-----------------------

Yes.  One format, one file, and both kinds of cheat run in both programs.

Most cheats are plain codes, applied by the emulator core itself:

    cheat0_desc   = "Infinite lives"
    cheat0_code   = "AAAA-BBBB"
    cheat0_enable = "true"

The other kind is applied by the frontend, which writes a value straight
into the emulated machine's memory once per frame.  Those carry no code --
cheat0_address, cheat0_value and cheat0_cheat_type are the cheat -- and are
what RetroArch's memory searcher produces.  REG-Station runs them as well,
including the increase and decrease types, the conditional ones that gate
the cheat listed after them, the repeat blocks and the rumble triggers.

What REG-Station does not have is a memory searcher, so it can use that
kind of cheat but not create one.  Make them in RetroArch and they will
work in both.

REG-Station also edits the file in place rather than rewriting it: it
changes the cheat<N>_enable lines and copies everything else through
untouched, comments and ordering included.

Core names
----------

Folder name                      Core file
a5200                            a5200_libretro.so
Amiberry                         amiberry_libretro.so
AppleWin                         applewin_libretro.so
arduous                          arduous_libretro.so
Atari800                         atari800_libretro.so
Azahar                           azahar_libretro.so
Beetle Lynx                      mednafen_lynx_libretro.so
Beetle NeoPop                    mednafen_ngp_libretro.so
Beetle PC-FX                     pcfx_libretro.so
Beetle PCE                       pce_libretro.so
Beetle PSX HW                    mednafen_psx_libretro.so
Beetle Saturn                    beetle-saturn_libretro.so
Beetle SuperGrafx                mednafen_supergrafx_libretro.so
Beetle VB                        vb_libretro.so
Beetle WonderSwan                mednafen_wswan_libretro.so
BlastEm                          blastem_libretro.so
blueMSX                          bluemsx_libretro.so
bsnes                            bsnes_libretro.so
bsnes-jg                         bsnes-jg_libretro.so
cap32                            cap32_libretro.so
CD-i (MAME)                      same_cdi_libretro.so
ClownMDEmu                       clownmdemu_libretro.so
DOSBox-pure                      dosbox_pure_libretro.so
EasyRPG Player                   easyrpg_libretro.so
FCEUmm                           fceumm_libretro.so
FinalBurn Neo                    fbneo_libretro.so
Flycast                          flycast_libretro.so
fMSX                             fmsx_libretro.so
FreeChaF                         freechaf_libretro.so
FreeIntv                         freeintv_libretro.so
fuse                             fuse_libretro.so
Gambatte                         gambatte_libretro.so
Game & Watch                     gw_libretro.so
Gearboy                          gearboy_libretro.so
Gearcoleco                       gearcoleco_libretro.so
Geargrafx                        geargrafx_libretro.so
Gearlynx                         gearlynx_libretro.so
Gearsystem                       gearsystem_libretro.so
Genesis Plus GX                  genesisplusgx_libretro.so
Geolith                          geolith_libretro.so
Handy                            handy_libretro.so
holani                           holani_libretro.so
jazz2                            jazz2_libretro.so
Kronos                           kronos_libretro.so
Libretro-EmuSCV                  emuscv_libretro.so
MAME                             mame_libretro.so
MAME 2003-Plus                   mame078plus_libretro.so
melonDS                          melonds_libretro.so
melonDS DS                       melondsds_libretro.so
Mesen                            mesen_libretro.so
Mesen-S                          mesen-s_libretro.so
mGBA                             mgba_libretro.so
Mini vMac                        minivmac_libretro.so
Mr.Boom                          mrboom_libretro.so
Mupen64Plus-Next                 mupen64plus-next_libretro.so
Neko Project II kai              np2kai_libretro.so
NeoCD                            neocd_libretro.so
Nestopia                         nestopia_libretro.so
NXEngine                         nxengine_libretro.so
O2EM                             o2em_libretro.so
Opera                            opera_libretro.so
Panda3DS                         panda3ds_libretro.so
ParaLLEl N64                     parallel_n64_libretro.so
PCSX-ReARMed                     pcsx_rearmed_libretro.so
PicoDrive                        picodrive_libretro.so
Play!                            play_libretro.so
PokeMini                         pokemini_libretro.so
Potator                          potator_libretro.so
PPSSPP                           ppsspp_libretro.so
PrBoom                           prboom_libretro.so
ProSystem                        prosystem_libretro.so
PUAE                             puae_libretro.so
PX68K                            px68k_libretro.so
QUASI88                          quasi88_libretro.so
REminiscence                     reminiscence_libretro.so
SameBoy                          sameboy_libretro.so
SameDuck                         sameduck_libretro.so
ScummVM                          scummvm_libretro.so
SMS Plus GX                      smsplus_libretro.so
Snes9x                           snes9x_libretro.so
Stella                           stella_libretro.so
Super Bros War                   superbroswar_libretro.so
Supermodel                       supermodel_libretro.so
SwanStation                      swanstation_libretro.so
theodore                         theodore_libretro.so
Uzem                             uzem_libretro.so
VBA-M                            vba-m_libretro.so
VecX                             vecx_libretro.so
VICE x128                        vice_x128_libretro.so
VICE x64                         vice_x64_libretro.so
VICE x64dtv                      vice_x64dtv_libretro.so
VICE x64sc                       vice_x64sc_libretro.so
VICE xpet                        vice_xpet_libretro.so
VICE xplus4                      vice_xplus4_libretro.so
VICE xscpu64                     vice_xscpu64_libretro.so
VICE xvic                        vice_xvic_libretro.so
Virtual Jaguar                   virtualjaguar_libretro.so
x1                               x1_libretro.so
xrick                            xrick_libretro.so
YabaSanshiro                     yabasanshiro_libretro.so
Zelda Classic v2.10              zc210_libretro.so
