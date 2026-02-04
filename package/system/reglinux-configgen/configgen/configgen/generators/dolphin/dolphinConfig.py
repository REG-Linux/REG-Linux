from enum import IntEnum
from os import environ
from pathlib import Path
from struct import pack, unpack
from typing import Any

from configgen.systemFiles import CONF, SAVES
from configgen.utils.logger import get_logger

DOLPHIN_CONFIG_DIR = Path(CONF) / "dolphin-emu"
DOLPHIN_CONFIG_PATH = DOLPHIN_CONFIG_DIR / "Dolphin.ini"
DOLPHIN_SAVES_DIR = Path(SAVES) / "dolphin-emu"
DOLPHIN_GFX_PATH = DOLPHIN_CONFIG_DIR / "GFX.ini"
DOLPHIN_SYSCONF_PATH = Path(DOLPHIN_SAVES_DIR) / "Wii" / "shared2" / "sys" / "SYSCONF"
DOLPHIN_BIN_PATH = "/usr/bin/dolphin-emu"

eslog = get_logger(__name__)


class ItemType(IntEnum):
    BIG_ARRAY = 1
    SMALL_ARRAY = 2
    BYTE = 3
    SHORT = 4
    LONG = 5
    LONG_LONG = 6
    BOOL = 7


def readBEInt16(f: Any) -> int:
    """Read a 16-bit big-endian integer from the file."""
    data = f.read(2)
    return unpack(">H", data)[0]


def readBEInt32(f: Any) -> int:
    """Read a 32-bit big-endian integer from the file."""
    data = f.read(4)
    return unpack(">L", data)[0]


def readBEInt64(f: Any) -> int:
    """Read a 64-bit big-endian integer from the file."""
    data = f.read(8)
    return unpack(">Q", data)[0]


def readBytes(f: Any, count: int) -> bytes:
    """Read a specified number of bytes from the file."""
    return f.read(count)


def readString(f: Any, length: int) -> str:
    """Read a string of specified length from the file."""
    data = f.read(length)
    return data.decode("utf-8")


def readInt8(f: Any) -> int:
    """Read an 8-bit signed integer from the file."""
    data = f.read(1)
    return unpack("b", data)[0]


def writeInt8(f: Any, value: int) -> None:
    """Write an 8-bit signed integer to the file."""
    data = pack("b", value)
    f.write(data)


def readWriteEntry(f: Any, setval: dict[str, Any]) -> None:
    """Read or write an entry in the SYSCONF file.

    Args:
        f: File object to read from or write to
        setval: Dictionary of values to set in the file

    """
    item_header = readInt8(f)
    item_type = ItemType((item_header & 0xE0) >> 5)
    item_name_length = (item_header & 0x1F) + 1
    item_name = readString(f, item_name_length)
    data_size = None

    if item_name in setval:
        if item_type == ItemType.BYTE:
            item_value = setval[item_name]
            writeInt8(f, item_value)
        else:
            raise ValueError(f"Item type {item_type} is not writable")
    elif item_type == ItemType.BIG_ARRAY:
        data_size = readBEInt16(f) + 1
        readBytes(f, data_size)
        item_value = "[Big Array]"
    elif item_type == ItemType.SMALL_ARRAY:
        data_size = readInt8(f) + 1
        readBytes(f, data_size)
        item_value = "[Small Array]"
    elif item_type == ItemType.BYTE:
        item_value = readInt8(f)
    elif item_type == ItemType.SHORT:
        item_value = readBEInt16(f)
    elif item_type == ItemType.LONG:
        item_value = readBEInt32(f)
    elif item_type == ItemType.LONG_LONG:
        item_value = readBEInt64(f)
        if data_size is not None:
            readBytes(f, data_size)
    elif item_type == ItemType.BOOL:
        item_value = readInt8(f)
    else:
        raise ValueError(f"Unknown item type: {item_type}")

    if not setval or item_name in setval:
        eslog.debug(f"{item_name:12s} = {item_value}")


def readWriteFile(filepath: str | Path, setval: dict[str, Any]) -> None:
    """Read or write the SYSCONF file.

    Args:
        filepath: Path to the file to read or write
        setval: Dictionary of values to set in the file

    """
    # Open in read or read/write depending on the action
    mode = "r+b" if setval else "rb"
    with Path(filepath).open(mode) as f:
        readString(f, 4)  # Read SCv0
        num_entries = readBEInt16(f)  # Number of entries
        offset_size = (num_entries + 1) * 2  # Offsets
        readBytes(f, offset_size)

        for _ in range(num_entries):  # Entries
            readWriteEntry(f, setval)


def getWiiLangFromEnvironment() -> int:
    """Get the Wii language from the environment."""
    lang = environ["LANG"][:5]
    available_languages = {
        "jp_JP": 0,
        "en_US": 1,
        "de_DE": 2,
        "fr_FR": 3,
        "es_ES": 4,
        "it_IT": 5,
        "nl_NL": 6,
        "zh_CN": 7,
        "zh_TW": 8,
        "ko_KR": 9,
    }
    return available_languages.get(lang, available_languages["en_US"])


def getRatioFromConfig(config: dict[str, Any], gameResolution: dict[str, int]) -> int:
    """Get the aspect ratio from the configuration.

    Args:
        config: Configuration dictionary
        gameResolution: Game resolution dictionary

    Returns:
        0 for 4:3, 1 for 16:9

    """
    # Sets the setting available to the Wii's internal NAND. Only has two values:
    # 0: 4:3 ; 1: 16:9
    if "tv_mode" in config:
        return 1 if config["tv_mode"] == "1" else 0
    return 0


def getSensorBarPosition(config: dict[str, Any]) -> int:
    """Get the sensor bar position from the configuration.

    Args:
        config: Configuration dictionary

    Returns:
        0 for BOTTOM, 1 for TOP

    """
    # Sets the setting available to the Wii's internal NAND. Only has two values:
    # 0: BOTTOM ; 1: TOP
    if "sensorbar_position" in config:
        return 1 if config["sensorbar_position"] == "1" else 0
    return 0


def updateConfig(
    config: dict[str, Any],
    filepath: str | Path,
    gameResolution: dict[str, int],
) -> None:
    """Update the SYSCONF file with the specified configuration.

    Args:
        config: Configuration dictionary
        filepath: Path to the SYSCONF file
        gameResolution: Game resolution dictionary

    """
    arg_setval = {
        "IPL.LNG": getWiiLangFromEnvironment(),
        "IPL.AR": getRatioFromConfig(config, gameResolution),
        "BT.BAR": getSensorBarPosition(config),
    }
    readWriteFile(filepath, arg_setval)


if __name__ == "__main__":
    readWriteFile(DOLPHIN_SYSCONF_PATH, {})
