#!/usr/bin/env python3

from generators.Generator import Generator
import Command
import os.path
from . import duckstationConfig

class DuckstationGenerator(Generator):
    # Duckstation is now QT-only, requires wayland compositor to run
    def requiresWayland(self):
        return True

    def generate(self, system, rom, playersControllers, metadata, guns, wheels, gameResolution):

        duckstationConfig.readWriteFile(system, playersControllers)

        # Test if it's a m3u file
        if os.path.splitext(rom)[1] == ".m3u":
            rom = rewriteM3uFullPath(rom)

        if os.path.exists(duckstationConfig.duckstationBin):
            commandArray = [duckstationConfig.duckstationBin, rom]
        else:
            commandArray = ["duckstation-nogui", "-batch", "-fullscreen", "--", rom]

        return Command.Command(array=commandArray)

def rewriteM3uFullPath(m3u):                                                                    # Rewrite a clean m3u file with valid fullpath
    # get initialm3u
    firstline = open(m3u).readline().rstrip()                                                   # Get first line in m3u
    initialfirstdisc = "/tmp/" + os.path.splitext(os.path.basename(firstline))[0] + ".m3u"      # Generating a temp path with the first iso filename in m3u

    # create a temp m3u to bypass Duckstation m3u bad pathfile
    fulldirname = os.path.dirname(m3u)
    initialm3u = open(m3u, "r")

    with open(initialfirstdisc, 'a') as f1:
        for line in initialm3u:
            if line[0] == "/":                          # for /MGScd1.chd
                newpath = fulldirname + line
            else:
                newpath = fulldirname + "/" + line      # for MGScd1.chd
            f1.write(newpath)

    return initialfirstdisc
