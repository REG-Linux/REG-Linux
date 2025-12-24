from .gzdoomConfig import GZDOOM_CONFIG_PATH


def setGzdoomControllers(system):
    with open(GZDOOM_CONFIG_PATH) as file:
        lines = file.readlines()

    if system.isOptSet("gz_joystick"):
        # Enable the joystick for configuration in GZDoom by the user currently
        set_gz_joystick = system.config["gz_joystick"]
    else:
        set_gz_joystick = "false"

    joystick_line_found = False
    for i, line in enumerate(lines):
        if "use_joystick" in line:
            lines[i] = f"use_joystick={set_gz_joystick}\n"
            joystick_line_found = True
            break

    if not joystick_line_found:
        if "[GlobalSettings]" not in lines:
            lines.append("[GlobalSettings]\n")
            lines.append(f"use_joystick={set_gz_joystick}\n")
        else:
            for i, line in enumerate(lines):
                if line.strip() == "[GlobalSettings]":
                    lines.insert(i + 1, f"use_joystick={set_gz_joystick}\n")

    with open(GZDOOM_CONFIG_PATH, "w") as file:
        file.writelines(lines)
