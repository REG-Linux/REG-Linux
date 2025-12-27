from pathlib import Path

from configgen.systemFiles import CONF, SAVES

dolphinTriforceConfig = str(Path(CONF) / "dolphin-triforce")
dolphinTriforceData = str(Path(SAVES) / "dolphin-triforce")
dolphinTriforceIni = str(Path(dolphinTriforceConfig) / "Config" / "Dolphin.ini")
dolphinTriforceGfxIni = str(Path(dolphinTriforceConfig) / "Config" / "gfx_opengl.ini")
dolphinTriforceLoggerIni = str(Path(dolphinTriforceConfig) / "Config" / "Logger.ini")
dolphinTriforceGameSettings = str(Path(dolphinTriforceConfig) / "GameSettings")
