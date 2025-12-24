from glob import glob
from os import makedirs, path, symlink
from re import compile
from shutil import copy

from configgen.Command import Command
from configgen.controllers import generate_sdl_controller_config
from configgen.generators.Generator import Generator
from configgen.systemFiles import ROMS

XASH3D_ROMS_DIR = ROMS + "/xash3d_fwgs"
XASH3D_HLSDK_LIBS_DIR = "/usr/lib/xash3d/hlsdk"
XASH3D_DEFAULT_SERVER_LIB = "hl"
XASH3D_BIN_PATH = "/usr/bin/xash3d"


def _rom_dir(game):
    return XASH3D_ROMS_DIR + "/" + game


def _config_dir(game):
    return "/userdata/system/configs/xash3d_fwgs/" + game


def _save_dir(game):
    return "/userdata/saves/xash3d_fwgs/" + game


def _client_lib_path(server_lib, arch_suffix):
    return (
        XASH3D_HLSDK_LIBS_DIR
        + "/"
        + server_lib
        + "/cl_dlls/client"
        + arch_suffix
        + ".so"
    )


def _server_lib_path(server_lib, arch_suffix):
    return (
        XASH3D_HLSDK_LIBS_DIR
        + "/"
        + server_lib
        + "/dlls/"
        + server_lib
        + arch_suffix
        + ".so"
    )


def _get_server_lib_basename_from_liblist_gam(game):
    """Gets the base name of the server library from liblist.gam in the game directory."""
    file = _rom_dir(game) + "/liblist.gam"
    if not path.exists(file):
        return None
    pattern = compile(r'gamedll\w*\s+"(?:dlls[/\\])?([^.]*)')
    with open(file) as f:
        for line in f:
            m = pattern.match(line)
            if m:
                return m.group(1)
    return None


def _find_server_lib(server_lib, arch_suffix):
    """Finds and returns the server library.

    Falls back to XASH3D_DEFAULT_SERVER_LIB if none is found.
    """
    if server_lib:
        file = _server_lib_path(server_lib, arch_suffix)
        if path.exists(file):
            return file

    return _server_lib_path(XASH3D_DEFAULT_SERVER_LIB, arch_suffix)


def _find_client_lib(server_lib, arch_suffix):
    """Finds and returns the client library.

    Falls back to the client library for XASH3D_DEFAULT_SERVER_LIB if none is found.
    """
    if server_lib:
        file = _client_lib_path(server_lib, arch_suffix)
        if path.exists(file):
            return file

    return _client_lib_path(XASH3D_DEFAULT_SERVER_LIB, arch_suffix)


def _get_arch_suffix():
    """Returns the architecture suffix, e.g. _amd64, based on a known server library."""
    path_prefix = XASH3D_HLSDK_LIBS_DIR + "/hl/dlls/hl"
    return glob(path_prefix + "*.so")[0][len(path_prefix) : -3]


class Xash3dFwgsGenerator(Generator):
    def generate(
        self, system, rom, players_controllers, metadata, guns, wheels, game_resolution
    ):
        game = path.splitext(path.basename(rom))[0]

        arch_suffix = _get_arch_suffix()
        server_lib = _get_server_lib_basename_from_liblist_gam(game)

        # Useful options for debugging:
        # -log        # Log to /userdata/roms/xash3d_fwgs/engine.log
        # -dev 2      # Verbose logging
        # -ref gles2  # Select a specific renderer (gl, gl4es, gles1, gles2, soft)
        command_array = [XASH3D_BIN_PATH, "-fullscreen", "-dev"]

        # By default, xash3d will use `dlls/hl.so` in the valve directory (via the `liblist.gam` config file).
        # However, that `so` is incompatible with xash3d (it's the x86-glibc version from Valve).
        # We instead point to the hlsdk-xash3d `so`.
        command_array.append("-clientlib")
        command_array.append(_find_client_lib(server_lib, arch_suffix))

        command_array.append("-dll")
        command_array.append(_find_server_lib(server_lib, arch_suffix))

        command_array.append("-game")
        command_array.append(game)

        command_array.append("+showfps")
        command_array.append("1" if system.getOptBoolean("showFPS") else "0")

        self._maybeInitConfig(game)
        self._maybeInitSaveDir(game)

        return Command(
            array=command_array,
            env={
                "XASH3D_BASEDIR": XASH3D_ROMS_DIR,
                "XASH3D_EXTRAS_PAK1": "/usr/share/xash3d/valve/extras.pk3",
                "LD_LIBRARY_PATH": "/usr/lib/xash3d",
                "SDL_GAMECONTROLLERCONFIG": generate_sdl_controller_config(
                    players_controllers
                ),
            },
        )

    def _maybeInitConfig(self, game):
        rom_dir = _rom_dir(game)
        if not path.exists(rom_dir + "/userconfig.cfg"):
            with open(rom_dir + "/userconfig.cfg", "w") as f:
                f.write("exec gamepad.cfg\nexec custom.cfg\n")

        if not path.exists(rom_dir + "/gamepad.cfg"):
            copy(
                path.dirname(path.abspath(__file__)) + "/gamepad.cfg",
                rom_dir + "/gamepad.cfg",
            )

        config_dir = _config_dir(game)
        if not path.exists(config_dir + "/custom.cfg"):
            if not path.exists(config_dir):
                makedirs(config_dir)
            with open(config_dir + "/custom.cfg", "w") as f:
                f.write("\n")
            if not path.exists(rom_dir + "/custom.cfg"):
                symlink(config_dir + "/custom.cfg", rom_dir + "/custom.cfg")

    def _maybeInitSaveDir(self, game):
        rom_dir = _rom_dir(game)
        if not path.isdir(rom_dir + "/save"):
            save_dir = _save_dir(game)
            if not path.exists(save_dir):
                makedirs(save_dir)
            if not path.exists(rom_dir + "/save"):
                symlink(save_dir, rom_dir + "/save")
