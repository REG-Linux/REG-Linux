from configgen.utils.logger import get_logger

eslog = get_logger(__name__)


def setCgeniusControllers(cgeniusConfig, playersControllers):
    CGENIUS_CTRL = {
        "a": "Fire",
        "b": "Jump",
        "leftshoulder": "Camlead",
        "x": "Status",
        "y": "Pogo",
        "rightshoulder": "Run",
        "dpup": "Up",
        "dpdown": "Down",
        "dpleft": "Left",
        "dpright": "Right",
        "back": "Back",
    }

    # -= Controllers =-
    # Configure the first four controllers
    nplayer = 1
    for playercontroller, pad in sorted(playersControllers.items()):
        if nplayer < 4:
            input_num = "input" + str(pad.index)
            if input_num not in cgeniusConfig:
                cgeniusConfig[input_num] = {}
            for x in pad.inputs:
                input = pad.inputs[x]
                if input.name in CGENIUS_CTRL:
                    if input.type == "hat":
                        cgeniusConfig[input_num][CGENIUS_CTRL[input.name]] = (
                            "Joy"
                            + str(pad.index)
                            + "-"
                            + input.type[0].upper()
                            + str(input.id[-1])
                        )
                    else:
                        cgeniusConfig[input_num][CGENIUS_CTRL[input.name]] = (
                            "Joy"
                            + str(pad.index)
                            + "-"
                            + input.type[0].upper()
                            + str(input.id)
                        )
            nplayer += 1
