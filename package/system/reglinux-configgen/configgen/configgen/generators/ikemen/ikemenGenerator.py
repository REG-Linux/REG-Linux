from generators.Generator import Generator
from Command import Command
from json import load, dumps
from os import path, mkdir
from .ikemenControllers import Keymapping, Joymapping

IKEMEN_BIN_PATH = '/usr/bin/system-ikemen'

class IkemenGenerator(Generator):

    def generate(self, system, rom, playersControllers, metadata, guns, wheels, gameResolution):
        try:
            conf = load(open(rom+"/save/config.json", "r"))
        except:
            conf = {}

        # Joystick configuration seems completely broken in 0.98.2 Linux
        # so let's force keyboad and use a pad2key
        conf["KeyConfig"] = Keymapping
        conf["JoystickConfig"] = Joymapping
        conf["Fullscreen"] = True

        js_out = dumps(conf, indent=2)
        if not path.isdir(rom+"/save"):
            mkdir(rom+"/save")
        with open(rom+"/save/config.json", "w") as jout:
            jout.write(js_out)

        commandArray = [IKEMEN_BIN_PATH, rom]

        return Command(array=commandArray)
