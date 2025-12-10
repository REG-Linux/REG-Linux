from configgen.generators.Generator import Generator
from configgen.Command import Command


class OdcommanderGenerator(Generator):
    def generate(
        self, system, rom, playersControllers, metadata, guns, wheels, gameResolution
    ):
        commandArray = ["od-commander"]

        return Command(array=commandArray)
