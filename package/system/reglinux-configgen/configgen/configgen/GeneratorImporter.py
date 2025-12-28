"""
GeneratorImporter module provides functionality to dynamically import and instantiate
generator classes for various emulators based on a predefined mapping.
"""

from importlib import import_module
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .generators.Generator import Generator


class GeneratorNotFoundError(Exception):
    """Exception raised when no generator is found for the specified emulator."""

    pass


# Mapping of emulator names to their respective module paths and class names
EMULATOR_MAPPING = {
    "abuse": ("configgen.generators.abuse.abuseGenerator", "AbuseGenerator"),
    "amiberry": (
        "configgen.generators.amiberry.amiberryGenerator",
        "AmiberryGenerator",
    ),
    "applewin": (
        "configgen.generators.applewin.applewinGenerator",
        "AppleWinGenerator",
    ),
    "azahar": ("configgen.generators.azahar.azaharGenerator", "AzaharGenerator"),
    "bigpemu": ("configgen.generators.bigpemu.bigpemuGenerator", "BigPEmuGenerator"),
    "cannonball": (
        "configgen.generators.cannonball.cannonballGenerator",
        "CannonballGenerator",
    ),
    "cdogs": ("configgen.generators.cdogs.cdogsGenerator", "CdogsGenerator"),
    "cemu": ("configgen.generators.cemu.cemuGenerator", "CemuGenerator"),
    "cgenius": ("configgen.generators.cgenius.cgeniusGenerator", "CGeniusGenerator"),
    "eden": ("configgen.generators.eden.edenGenerator", "EdenGenerator"),
    "corsixth": (
        "configgen.generators.corsixth.corsixthGenerator",
        "CorsixTHGenerator",
    ),
    "devilutionx": (
        "generators.devilutionx.devilutionxGenerator",
        "DevilutionXGenerator",
    ),
    "dhewm3": ("configgen.generators.dhewm3.dhewm3Generator", "Dhewm3Generator"),
    "dolphin": ("configgen.generators.dolphin.dolphinGenerator", "DolphinGenerator"),
    "dolphin_triforce": (
        "generators.dolphin_triforce.dolphinTriforceGenerator",
        "DolphinTriforceGenerator",
    ),
    "dosbox_staging": (
        "generators.dosboxstaging.dosboxstagingGenerator",
        "DosBoxStagingGenerator",
    ),
    "dosboxx": ("configgen.generators.dosboxx.dosboxxGenerator", "DosBoxxGenerator"),
    "drastic": ("configgen.generators.drastic.drasticGenerator", "DrasticGenerator"),
    "duckstation": (
        "generators.duckstation.duckstationGenerator",
        "DuckstationGenerator",
    ),
    "dxx-rebirth": (
        "generators.dxx_rebirth.dxx_rebirthGenerator",
        "DXX_RebirthGenerator",
    ),
    "easyrpg": ("configgen.generators.easyrpg.easyrpgGenerator", "EasyRPGGenerator"),
    "ecwolf": ("configgen.generators.ecwolf.ecwolfGenerator", "ECWolfGenerator"),
    "eduke32": ("configgen.generators.eduke32.eduke32Generator", "EDuke32Generator"),
    "etlegacy": (
        "configgen.generators.etlegacy.etlegacyGenerator",
        "ETLegacyGenerator",
    ),
    "fallout1-ce": (
        "configgen.generators.fallout1.fallout1Generator",
        "Fallout1Generator",
    ),
    "fallout2-ce": (
        "configgen.generators.fallout2.fallout2Generator",
        "Fallout2Generator",
    ),
    "flycast": ("configgen.generators.flycast.flycastGenerator", "FlycastGenerator"),
    "gsplus": ("configgen.generators.gsplus.gsplusGenerator", "GSplusGenerator"),
    "gzdoom": ("configgen.generators.gzdoom.gzdoomGenerator", "GZDoomGenerator"),
    "hcl": ("configgen.generators.hcl.hclGenerator", "HclGenerator"),
    "hatari": ("configgen.generators.hatari.hatariGenerator", "HatariGenerator"),
    "hurrican": (
        "configgen.generators.hurrican.hurricanGenerator",
        "HurricanGenerator",
    ),
    "hypseus-singe": (
        "generators.hypseus_singe.hypseusSingeGenerator",
        "HypseusSingeGenerator",
    ),
    "ikemen": ("configgen.generators.ikemen.ikemenGenerator", "IkemenGenerator"),
    "iortcw": ("configgen.generators.iortcw.iortcwGenerator", "IORTCWGenerator"),
    "ioquake3": (
        "configgen.generators.ioquake3.ioquake3Generator",
        "IOQuake3Generator",
    ),
    "jazz2": ("configgen.generators.jazz2.jazz2Generator", "Jazz2Generator"),
    "lightspark": (
        "configgen.generators.lightspark.lightsparkGenerator",
        "LightsparkGenerator",
    ),
    "libretro": (
        "configgen.generators.libretro.libretroGenerator",
        "LibretroGenerator",
    ),
    "mame": ("configgen.generators.mame.mameGenerator", "MameGenerator"),
    "mednafen": (
        "configgen.generators.mednafen.mednafenGenerator",
        "MednafenGenerator",
    ),
    "melonds": ("configgen.generators.melonds.melondsGenerator", "MelonDSGenerator"),
    "moonlight": (
        "configgen.generators.moonlight.moonlightGenerator",
        "MoonlightGenerator",
    ),
    "mupen64plus": ("configgen.generators.mupen.mupenGenerator", "MupenGenerator"),
    "odcommander": (
        "generators.odcommander.odcommanderGenerator",
        "OdcommanderGenerator",
    ),
    "openbor": ("configgen.generators.openbor.openborGenerator", "OpenborGenerator"),
    "openjazz": (
        "configgen.generators.openjazz.openjazzGenerator",
        "OpenJazzGenerator",
    ),
    "openmsx": ("configgen.generators.openmsx.openmsxGenerator", "OpenmsxGenerator"),
    "pcsx2": ("configgen.generators.pcsx2.pcsx2Generator", "Pcsx2Generator"),
    "play": ("configgen.generators.play.playGenerator", "PlayGenerator"),
    "ppsspp": ("configgen.generators.ppsspp.ppssppGenerator", "PPSSPPGenerator"),
    "raze": ("configgen.generators.raze.razeGenerator", "RazeGenerator"),
    "rpcs3": ("configgen.generators.rpcs3.rpcs3Generator", "Rpcs3Generator"),
    "ruffle": ("configgen.generators.ruffle.ruffleGenerator", "RuffleGenerator"),
    "ryujinx": ("configgen.generators.ryujinx.ryujinxGenerator", "RyujinxGenerator"),
    "samcoupe": (
        "configgen.generators.samcoupe.samcoupeGenerator",
        "SamcoupeGenerator",
    ),
    "scummvm": ("configgen.generators.scummvm.scummvmGenerator", "ScummVMGenerator"),
    "sdlpop": ("configgen.generators.sdlpop.sdlpopGenerator", "SdlPopGenerator"),
    "sh": ("configgen.generators.sh.shGenerator", "ShGenerator"),
    "solarus": ("configgen.generators.solarus.solarusGenerator", "SolarusGenerator"),
    "shadps4": ("configgen.generators.shadps4.shadps4Generator", "Shadps4Generator"),
    "sonic-mania": (
        "generators.sonic_mania.sonic_maniaGenerator",
        "SonicManiaGenerator",
    ),
    "sonic2013": (
        "configgen.generators.sonicretro.sonicretroGenerator",
        "SonicRetroGenerator",
    ),
    "sonic3-air": (
        "configgen.generators.sonic3_air.sonic3_airGenerator",
        "Sonic3AIRGenerator",
    ),
    "soniccd": (
        "configgen.generators.sonicretro.sonicretroGenerator",
        "SonicRetroGenerator",
    ),
    "stella": ("configgen.generators.stella.stellaGenerator", "StellaGenerator"),
    "steam": ("configgen.generators.steam.steamGenerator", "SteamGenerator"),
    "supermodel": (
        "configgen.generators.supermodel.supermodelGenerator",
        "SupermodelGenerator",
    ),
    "taradino": (
        "configgen.generators.taradino.taradinoGenerator",
        "TaradinoGenerator",
    ),
    "theforceengine": (
        "generators.theforceengine.theforceengineGenerator",
        "TheForceEngineGenerator",
    ),
    "thextech": (
        "configgen.generators.thextech.thextechGenerator",
        "TheXTechGenerator",
    ),
    "tsugaru": ("configgen.generators.tsugaru.tsugaruGenerator", "TsugaruGenerator"),
    "tyrian": ("configgen.generators.tyrian.tyrianGenerator", "TyrianGenerator"),
    "uqm": ("configgen.generators.uqm.uqmGenerator", "UqmGenerator"),
    "vice": ("configgen.generators.vice.viceGenerator", "ViceGenerator"),
    "vita3k": ("configgen.generators.vita3k.vita3kGenerator", "Vita3kGenerator"),
    "vpinball": (
        "configgen.generators.vpinball.vpinballGenerator",
        "VPinballGenerator",
    ),
    "xash3d_fwgs": (
        "generators.xash3d_fwgs.xash3dFwgsGenerator",
        "Xash3dFwgsGenerator",
    ),
    "xemu": ("configgen.generators.xemu.xemuGenerator", "XemuGenerator"),
    "xenia-canary": ("configgen.generators.xenia.xeniaGenerator", "XeniaGenerator"),
}

PRELOADED_GENERATORS: dict[str, type["Generator"]] = {}


def _load_generator_class(emulator: str) -> type["Generator"]:
    try:
        module_path, class_name = EMULATOR_MAPPING[emulator]
    except KeyError:
        raise GeneratorNotFoundError(
            f"No generator found for emulator {emulator}"
        ) from None

    module = import_module(module_path)
    return getattr(module, class_name)


def getGenerator(emulator: str) -> "Generator":
    """
    Returns an instance of the appropriate generator class for the specified emulator.

    Args:
        emulator (str): The name of the emulator for which to retrieve the generator.

    Returns:
        object: An instance of the generator class corresponding to the emulator.

    Raises:
        GeneratorNotFoundError: If no generator is found for the specified emulator.
    """
    generator_class: type[Generator] | None = PRELOADED_GENERATORS.get(emulator)
    if generator_class is None:
        try:
            generator_class = _load_generator_class(emulator)
        except ImportError as e:
            raise GeneratorNotFoundError(
                f"Failed to import generator for {emulator}: {e}"
            ) from e
        except AttributeError as e:
            raise GeneratorNotFoundError(
                f"Generator class not found for {emulator}: {e}"
            ) from e
        PRELOADED_GENERATORS[emulator] = generator_class

    return generator_class()
