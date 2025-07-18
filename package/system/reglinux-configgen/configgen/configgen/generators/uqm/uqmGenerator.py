#!/usr/bin/env python3

from generators.Generator import Generator
import os
import Command

class UqmGenerator(Generator):

    def generate(self, system, rom, playersControllers, metadata, guns, wheels, gameResolution):
        directories = [
            '/userdata/saves/uqm',
            '/userdata/saves/uqm/teams',
            '/userdata/saves/uqm/save'
        ]

        for directory in directories:
            os.makedirs(directory, exist_ok=True)

        with open('/userdata/roms/uqm/version', 'a'): # Create file if does not exist
            pass

        commandArray = ["urquan","--contentdir=/userdata/roms/uqm",
                        "--configdir=/userdata/saves/uqm"]

        return Command.Command(array=commandArray)
