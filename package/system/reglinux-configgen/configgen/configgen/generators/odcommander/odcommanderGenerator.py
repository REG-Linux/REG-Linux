from configgen.command import Command
from configgen.generators.generator import Generator


class OdcommanderGenerator(Generator):
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
        command_array = ["od-commander"]

        return Command(array=command_array)
