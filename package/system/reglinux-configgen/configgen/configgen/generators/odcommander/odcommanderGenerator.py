from configgen.Command import Command
from configgen.generators.Generator import Generator


class OdcommanderGenerator(Generator):
    def generate(
        self, system, rom, players_controllers, metadata, guns, wheels, game_resolution,
    ):
        command_array = ["od-commander"]

        return Command(array=command_array)
