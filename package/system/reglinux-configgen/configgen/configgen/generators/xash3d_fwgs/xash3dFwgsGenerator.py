from glob import glob
from pathlib import Path
from re import compile as re_compile
from shutil import copy

from configgen.command import Command
from configgen.controllers import generate_sdl_controller_config
from configgen.generators.generator import Generator
from configgen.systemFiles import ROMS

XASH3D_ROMS_DIR = ROMS / "xash3d_fwgs"
XASH3D_HLSDK_LIBS_DIR = Path("/usr/lib/xash3d/hlsdk")
XASH3D_DEFAULT_SERVER_LIB = "hl"
XASH3D_BIN_PATH = Path("/usr/bin/xash3d")


def _rom_dir(game: str) -> Path:
    return XASH3D_ROMS_DIR / game


def _config_dir(game: str) -> Path:
    return Path("/userdata/system/configs/xash3d_fwgs") / game


def _save_dir(game: str) -> Path:
    return Path("/userdata/saves/xash3d_fwgs") / game


def _client_lib_path(server_lib: str, arch_suffix: str) -> Path:
    return XASH3D_HLSDK_LIBS_DIR / server_lib / "cl_dlls" / f"client{arch_suffix}.so"


def _server_lib_path(server_lib: str, arch_suffix: str) -> Path:
    return XASH3D_HLSDK_LIBS_DIR / server_lib / "dlls" / f"{server_lib}{arch_suffix}.so"


def _get_server_lib_basename_from_liblist_gam(game: str) -> str | None:
    """Get the base name of the server library from liblist.gam in the game directory."""
    file_path = _rom_dir(game) / "liblist.gam"
    if not file_path.exists():
        return None
    pattern = re_compile(r'gamedll\w*\s+"(?:dlls[/\\])?([^.]*)')
    with Path(file_path).open(encoding="utf-8") as f:
        for line in f:
            m = pattern.match(line)
            if m:
                return m.group(1)
    return None


def _find_server_lib(server_lib: str | None, arch_suffix: str) -> Path:
    """Find and return the server library.

    Falls back to XASH3D_DEFAULT_SERVER_LIB if none is found.
    """
    if server_lib:
        file_path = _server_lib_path(server_lib, arch_suffix)
        if file_path.exists():
            return file_path

    return _server_lib_path(XASH3D_DEFAULT_SERVER_LIB, arch_suffix)


def _find_client_lib(server_lib: str | None, arch_suffix: str) -> Path:
    """Find and return the client library.

    Falls back to the client library for XASH3D_DEFAULT_SERVER_LIB if none is found.
    """
    if server_lib:
        file_path = _client_lib_path(server_lib, arch_suffix)
        if file_path.exists():
            return file_path

    return _client_lib_path(XASH3D_DEFAULT_SERVER_LIB, arch_suffix)


def _get_arch_suffix():
    """Return the architecture suffix, e.g. _amd64, based on a known server library."""
    path_prefix = XASH3D_HLSDK_LIBS_DIR / "hl" / "dlls" / "hl"
    return glob(str(path_prefix) + "*.so")[0][len(str(path_prefix)) : -3]


class Xash3dFwgsGenerator(Generator):
    def generate(
        self,
        system,
        rom,
        players_controllers,
        metadata,
        guns,
        wheels,
        game_resolution,
    ):
        game = Path(rom).stem

        arch_suffix = _get_arch_suffix()
        server_lib = _get_server_lib_basename_from_liblist_gam(game)

        # Useful options for debugging:
        # -log        # Log to /userdata/roms/xash3d_fwgs/engine.log
        # -dev 2      # Verbose logging
        # -ref gles2  # Select a specific renderer (gl, gl4es, gles1, gles2, soft)
        command_array = [str(XASH3D_BIN_PATH), "-fullscreen", "-dev"]

        # By default, xash3d will use `dlls/hl.so` in the valve directory (via the `liblist.gam` config file).
        # However, that `so` is incompatible with xash3d (it's the x86-glibc version from Valve).
        # We instead point to the hlsdk-xash3d `so`.
        command_array.append("-clientlib")
        command_array.append(str(_find_client_lib(server_lib, arch_suffix)))

        command_array.append("-dll")
        command_array.append(str(_find_server_lib(server_lib, arch_suffix)))

        command_array.append("-game")
        command_array.append(game)

        command_array.append("+showfps")
        command_array.append("1" if system.getOptBoolean("showFPS") else "0")

        self._maybeInitConfig(game)
        self._maybeInitSaveDir(game)

        return Command(
            array=command_array,
            env={
                "XASH3D_BASEDIR": str(XASH3D_ROMS_DIR),
                "XASH3D_EXTRAS_PAK1": "/usr/share/xash3d/valve/extras.pk3",
                "LD_LIBRARY_PATH": "/usr/lib/xash3d",
                "SDL_GAMECONTROLLERCONFIG": generate_sdl_controller_config(
                    players_controllers,
                ),
            },
        )

    def _maybeInitConfig(self, game: str) -> None:
        rom_dir = _rom_dir(game)
        userconfig_path = rom_dir / "userconfig.cfg"
        if not userconfig_path.exists():
            Path(userconfig_path).write_text(
                "exec gamepad.cfg\nexec custom.cfg\n", encoding="utf-8"
            )

        gamepad_path = rom_dir / "gamepad.cfg"
        if not gamepad_path.exists():
            current_dir = Path(__file__).parent
            copy(
                str(current_dir / "gamepad.cfg"),
                str(gamepad_path),
            )

        config_dir = _config_dir(game)
        custom_cfg_path = config_dir / "custom.cfg"
        if not custom_cfg_path.exists():
            if not config_dir.exists():
                config_dir.mkdir(parents=True, exist_ok=True)
            Path(custom_cfg_path).write_text("\n", encoding="utf-8")
            rom_custom_cfg_path = rom_dir / "custom.cfg"
            if not rom_custom_cfg_path.exists():
                Path(str(rom_custom_cfg_path)).symlink_to(str(custom_cfg_path))

    def _maybeInitSaveDir(self, game: str) -> None:
        rom_dir = _rom_dir(game)
        save_path = rom_dir / "save"
        if not save_path.is_dir():
            save_dir = _save_dir(game)
            if not save_dir.exists():
                save_dir.mkdir(parents=True, exist_ok=True)
            if not save_path.exists():
                Path(str(save_path)).symlink_to(str(save_dir))
