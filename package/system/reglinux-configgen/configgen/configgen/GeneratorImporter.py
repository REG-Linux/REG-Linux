"""
GeneratorImporter module provides functionality to dynamically import and instantiate
generator classes for various emulators based on a predefined mapping.
"""

from importlib import import_module


class GeneratorNotFoundError(Exception):
    """Exception raised when no generator is found for the specified emulator."""

    pass


# Mapping of emulator names to their respective module paths and class names
EMULATOR_MAPPING = {
    "abuse": ("generators.abuse.abuseGenerator", "AbuseGenerator"),
    "amiberry": ("generators.amiberry.amiberryGenerator", "AmiberryGenerator"),
    "applewin": ("generators.applewin.applewinGenerator", "AppleWinGenerator"),
    "azahar": ("generators.azahar.azaharGenerator", "AzaharGenerator"),
    "bigpemu": ("generators.bigpemu.bigpemuGenerator", "BigPEmuGenerator"),
    "cannonball": ("generators.cannonball.cannonballGenerator", "CannonballGenerator"),
    "cdogs": ("generators.cdogs.cdogsGenerator", "CdogsGenerator"),
    "cemu": ("generators.cemu.cemuGenerator", "CemuGenerator"),
    "cgenius": ("generators.cgenius.cgeniusGenerator", "CGeniusGenerator"),
    "eden": ("generators.eden.edenGenerator", "EdenGenerator"),
    "corsixth": ("generators.corsixth.corsixthGenerator", "CorsixTHGenerator"),
    "devilutionx": (
        "generators.devilutionx.devilutionxGenerator",
        "DevilutionXGenerator",
    ),
    "dhewm3": ("generators.dhewm3.dhewm3Generator", "Dhewm3Generator"),
    "dolphin": ("generators.dolphin.dolphinGenerator", "DolphinGenerator"),
    "dolphin_triforce": (
        "generators.dolphin_triforce.dolphinTriforceGenerator",
        "DolphinTriforceGenerator",
    ),
    "dosbox_staging": (
        "generators.dosboxstaging.dosboxstagingGenerator",
        "DosBoxStagingGenerator",
    ),
    "dosboxx": ("generators.dosboxx.dosboxxGenerator", "DosBoxxGenerator"),
    "drastic": ("generators.drastic.drasticGenerator", "DrasticGenerator"),
    "duckstation": (
        "generators.duckstation.duckstationGenerator",
        "DuckstationGenerator",
    ),
    "dxx-rebirth": (
        "generators.dxx_rebirth.dxx_rebirthGenerator",
        "DXX_RebirthGenerator",
    ),
    "easyrpg": ("generators.easyrpg.easyrpgGenerator", "EasyRPGGenerator"),
    "ecwolf": ("generators.ecwolf.ecwolfGenerator", "ECWolfGenerator"),
    "eduke32": ("generators.eduke32.eduke32Generator", "EDuke32Generator"),
    "etlegacy": ("generators.etlegacy.etlegacyGenerator", "ETLegacyGenerator"),
    "fallout1-ce": ("generators.fallout1.fallout1Generator", "Fallout1Generator"),
    "fallout2-ce": ("generators.fallout2.fallout2Generator", "Fallout2Generator"),
    "flycast": ("generators.flycast.flycastGenerator", "FlycastGenerator"),
    "gsplus": ("generators.gsplus.gsplusGenerator", "GSplusGenerator"),
    "gzdoom": ("generators.gzdoom.gzdoomGenerator", "GZDoomGenerator"),
    "hcl": ("generators.hcl.hclGenerator", "HclGenerator"),
    "hatari": ("generators.hatari.hatariGenerator", "HatariGenerator"),
    "hurrican": ("generators.hurrican.hurricanGenerator", "HurricanGenerator"),
    "hypseus-singe": (
        "generators.hypseus_singe.hypseusSingeGenerator",
        "HypseusSingeGenerator",
    ),
    "ikemen": ("generators.ikemen.ikemenGenerator", "IkemenGenerator"),
    "iortcw": ("generators.iortcw.iortcwGenerator", "IORTCWGenerator"),
    "ioquake3": ("generators.ioquake3.ioquake3Generator", "IOQuake3Generator"),
    "jazz2": ("generators.jazz2.jazz2Generator", "Jazz2Generator"),
    "lightspark": ("generators.lightspark.lightsparkGenerator", "LightsparkGenerator"),
    "libretro": ("generators.libretro.libretroGenerator", "LibretroGenerator"),
    "mame": ("generators.mame.mameGenerator", "MameGenerator"),
    "mednafen": ("generators.mednafen.mednafenGenerator", "MednafenGenerator"),
    "melonds": ("generators.melonds.melondsGenerator", "MelonDSGenerator"),
    "moonlight": ("generators.moonlight.moonlightGenerator", "MoonlightGenerator"),
    "mupen64plus": ("generators.mupen.mupenGenerator", "MupenGenerator"),
    "odcommander": (
        "generators.odcommander.odcommanderGenerator",
        "OdcommanderGenerator",
    ),
    "openbor": ("generators.openbor.openborGenerator", "OpenborGenerator"),
    "openjazz": ("generators.openjazz.openjazzGenerator", "OpenJazzGenerator"),
    "openmsx": ("generators.openmsx.openmsxGenerator", "OpenmsxGenerator"),
    "pcsx2": ("generators.pcsx2.pcsx2Generator", "Pcsx2Generator"),
    "play": ("generators.play.playGenerator", "PlayGenerator"),
    "ppsspp": ("generators.ppsspp.ppssppGenerator", "PPSSPPGenerator"),
    "raze": ("generators.raze.razeGenerator", "RazeGenerator"),
    "rpcs3": ("generators.rpcs3.rpcs3Generator", "Rpcs3Generator"),
    "ruffle": ("generators.ruffle.ruffleGenerator", "RuffleGenerator"),
    "ryujinx": ("generators.ryujinx.ryujinxGenerator", "RyujinxGenerator"),
    "samcoupe": ("generators.samcoupe.samcoupeGenerator", "SamcoupeGenerator"),
    "scummvm": ("generators.scummvm.scummvmGenerator", "ScummVMGenerator"),
    "sdlpop": ("generators.sdlpop.sdlpopGenerator", "SdlPopGenerator"),
    "sh": ("generators.sh.shGenerator", "ShGenerator"),
    "solarus": ("generators.solarus.solarusGenerator", "SolarusGenerator"),
    "shadps4": ("generators.shadps4.shadps4Generator", "Shadps4Generator"),
    "sonic-mania": (
        "generators.sonic_mania.sonic_maniaGenerator",
        "SonicManiaGenerator",
    ),
    "sonic2013": ("generators.sonicretro.sonicretroGenerator", "SonicRetroGenerator"),
    "sonic3-air": ("generators.sonic3_air.sonic3_airGenerator", "Sonic3AIRGenerator"),
    "soniccd": ("generators.sonicretro.sonicretroGenerator", "SonicRetroGenerator"),
    "stella": ("generators.stella.stellaGenerator", "StellaGenerator"),
    "steam": ("generators.steam.steamGenerator", "SteamGenerator"),
    "supermodel": ("generators.supermodel.supermodelGenerator", "SupermodelGenerator"),
    "taradino": ("generators.taradino.taradinoGenerator", "TaradinoGenerator"),
    "theforceengine": (
        "generators.theforceengine.theforceengineGenerator",
        "TheForceEngineGenerator",
    ),
    "thextech": ("generators.thextech.thextechGenerator", "TheXTechGenerator"),
    "tsugaru": ("generators.tsugaru.tsugaruGenerator", "TsugaruGenerator"),
    "tyrian": ("generators.tyrian.tyrianGenerator", "TyrianGenerator"),
    "uqm": ("generators.uqm.uqmGenerator", "UqmGenerator"),
    "vice": ("generators.vice.viceGenerator", "ViceGenerator"),
    "vita3k": ("generators.vita3k.vita3kGenerator", "Vita3kGenerator"),
    "vpinball": ("generators.vpinball.vpinballGenerator", "VPinballGenerator"),
    "xash3d_fwgs": (
        "generators.xash3d_fwgs.xash3dFwgsGenerator",
        "Xash3dFwgsGenerator",
    ),
    "xemu": ("generators.xemu.xemuGenerator", "XemuGenerator"),
    "xenia-canary": ("generators.xenia.xeniaGenerator", "XeniaGenerator"),
}

# Preload all generator classes
PRELOADED_GENERATORS = {}
for emulator, (module_path, class_name) in EMULATOR_MAPPING.items():
    try:
        module = import_module(module_path)
        PRELOADED_GENERATORS[emulator] = getattr(module, class_name)
    except (ImportError, AttributeError):
        continue  # Silence errors, or add logs if you want visibility


def getGenerator(emulator):
    """
    Returns an instance of the appropriate generator class for the specified emulator.

    Args:
        emulator (str): The name of the emulator for which to retrieve the generator.

    Returns:
        object: An instance of the generator class corresponding to the emulator.

    Raises:
        GeneratorNotFoundError: If no generator is found for the specified emulator.
    """
    try:
        generator_class = PRELOADED_GENERATORS[emulator]
        return generator_class()
    except KeyError:
        raise GeneratorNotFoundError(f"No generator found for emulator {emulator}")
