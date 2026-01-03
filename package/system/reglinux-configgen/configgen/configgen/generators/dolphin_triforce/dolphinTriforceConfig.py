from pathlib import Path

from configgen.systemFiles import CONF, SAVES

DOLPHIN_TRIFORCE_CONFIG_DIR = str(Path(CONF) / "dolphin-triforce")
DOLPHIN_TRIFORCE_SAVES_DIR = str(Path(SAVES) / "dolphin-triforce")
DOLPHIN_TRIFORCE_CONFIG_PATH = str(
    Path(DOLPHIN_TRIFORCE_CONFIG_DIR) / "Config" / "Dolphin.ini",
)
DOLPHIN_TRIFORCE_GFX_PATH = str(
    Path(DOLPHIN_TRIFORCE_CONFIG_DIR) / "Config" / "gfx_opengl.ini",
)
DOLPHIN_TRIFORCE_LOG_PATH = str(
    Path(DOLPHIN_TRIFORCE_CONFIG_DIR) / "Config" / "Logger.ini",
)
DOLPHIN_TRIFORCE_SETTINGS_DIR = str(Path(DOLPHIN_TRIFORCE_CONFIG_DIR) / "GameSettings")
