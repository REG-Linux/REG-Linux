from pathlib import Path
from typing import Any

from .viceConfig import VICE_CONTROLLER_PATH

# inputtype:
# 0      axis
# 1      button
# 2      hat
# 3      ball
#
# Note that each axis has 2 inputindex entries and each hat has 4.
#
# action [action_parameters]:
# 0               none
# 1 port pin      joystick (pin: 1/2/4/8/16/32/64/128/256/512/1024/2048 = u/d/l/r/fire(A)/fire2(B)/fire3(X)/Y/LB/RB/select/start)
# 2 row col       keyboard
# 3               map
# 4               UI activate
# 5 path&to&item  UI function
# 6 pot axis      joystick (pot: 1/2/3/4 = x1/y1/x2/y2)

viceJoystick = {
    "dpup": "# 2 0 / 1",
    "dpdown": "# 2 1 / 2",
    "dpleft": "# 2 2 / 4",
    "dpright": "# 2 3 / 8",
    "a": "# 1 ? / 16",
    "b": "# 1 ? / 32",
    "x": "# 1 ? / 64",
    "y": "# 1 ? / 128",
    "back": "# 1 ? 4",
    "leftshoulder": "# 1 ? 0",
    "rightshoulder": "# 1 ? 0",
}


# Create the controller configuration file
def setViceControllers(system: Any, playersControllers: Any) -> None:
    # vic20 uses a slightly different port
    joy_port = "0" if system.config["core"] == "xvic" else "1"

    controller_dir = Path(VICE_CONTROLLER_PATH).parent
    if not controller_dir.exists():
        controller_dir.mkdir(parents=True, exist_ok=True)

    listVice = []
    listVice.append("# REG-Linux configured controllers")
    listVice.append("")
    listVice.append("!CLEAR")
    nplayer = 1
    for _, pad in sorted(playersControllers.items()):
        listVice.append("")
        listVice.append("# " + pad.name)
        for x in pad.inputs:
            controller_input = pad.inputs[x]
            for indexName, indexValue in viceJoystick.items():
                if indexName == controller_input.name:
                    listVice.append(
                        indexValue.replace("#", str(pad.index))
                        .replace("?", str(controller_input.id))
                        .replace("/", joy_port),
                    )
        listVice.append("")
        nplayer += 1

    with open(VICE_CONTROLLER_PATH, "w") as f:
        f.writelines(str(listVice[i]) + "\n" for i in range(len(listVice)))
