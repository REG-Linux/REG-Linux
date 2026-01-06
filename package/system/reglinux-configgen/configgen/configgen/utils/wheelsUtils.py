from math import ceil, floor
from os import fdopen, kill, pipe
from re import match
from signal import SIGTERM
from subprocess import PIPE, Popen
from typing import Any

from evdev import device, ecodes

from configgen.utils.logger import get_logger

eslog = get_logger(__name__)

wheelMapping = {
    "wheel": "joystick1left",
    "accelerate": "r2",
    "brake": "l2",
    "downshift": "pageup",
    "upshift": "pagedown",
}

# partial mapping between real pads buttons and batocera pads
emulatorMapping = {
    "dreamcast": {"lt": "l2", "rt": "r2", "up": "pageup", "down": "pagedown"},
    "gamecube": {"lt": "l2", "rt": "r2", "a": "a", "b": "b", "x": "x", "y": "y"},
    "saturn": {
        "l": "l2",
        "r": "r2",
        "a": "b",
        "b": "a",
        "c": "pagedown",
        "x": "y",
        "y": "x",
        "z": "pageup",
        "start": "start",
    },
    "n64": {"l": "pageup", "r": "pagedown", "a": "b", "b": "y", "start": "start"},
    "wii": {"lt": "l2", "rt": "r2", "a": "a", "b": "b", "x": "x", "y": "y"},
    "wiiu": {
        "a": "a",
        "b": "b",
        "x": "x",
        "y": "y",
        "start": "start",
        "select": "select",
    },
    "psx": {
        "cross": "b",
        "square": "y",
        "round": "a",
        "triangle": "x",
        "start": "start",
        "select": "select",
    },
    "ps2": {"cross": "b", "square": "y", "round": "a", "triangle": "x"},
    "xbox": {"lt": "l2", "rt": "r2", "a": "b", "b": "a", "x": "y", "y": "x"},
}


def reconfigure_controllers(
    players_controllers: Any,
    system: Any,
    metadata: Any,
    device_list: Any,
) -> tuple[Any, Any, Any]:
    eslog.info("wheels reconfiguration")
    eslog.info("before wheel reconfiguration :")
    for _, pad in sorted(players_controllers.items()):
        eslog.info(
            "  "
            + str(pad.index)
            + ". index:"
            + str(pad.index)
            + " dev:"
            + pad.dev
            + " name:"
            + pad.name,
        )

    # reconfigure wheel buttons
    # no need to sort, but i like keeping the same loop (sorted by players)
    nplayer = 1
    for playercontroller, pad in sorted(players_controllers.items()):
        if pad.dev in device_list and device_list[pad.dev]["isWheel"]:
            eslog.info(f"Wheel reconfiguration for pad {pad.name}")
            original_inputs = pad.inputs.copy()

            # erase target keys
            for md in metadata:
                if md[:6] == "wheel_":
                    shortmd = md[6:]
                    if shortmd in wheelMapping and (
                        system.name in emulatorMapping
                        and metadata[md] in emulatorMapping[system.name]
                    ):
                        wheelkey = wheelMapping[shortmd]
                        if wheelkey in players_controllers[playercontroller].inputs:
                            del players_controllers[playercontroller].inputs[wheelkey]
                            eslog.info(f"wheel: erase the key {wheelkey}")

            # fill with the wanted keys
            for md in metadata:
                if md[:6] == "wheel_":
                    shortmd = md[6:]
                    if shortmd in wheelMapping and (
                        system.name in emulatorMapping
                        and metadata[md] in emulatorMapping[system.name]
                    ):
                        wheelkey = wheelMapping[shortmd]
                        wantedkey = emulatorMapping[system.name][metadata[md]]

                        if wheelkey in original_inputs:
                            players_controllers[playercontroller].inputs[wantedkey] = (
                                original_inputs[wheelkey]
                            )
                            players_controllers[playercontroller].inputs[
                                wantedkey
                            ].name = wantedkey
                            eslog.info(f"wheel: fill key {wantedkey} with {wheelkey}")
                        else:
                            eslog.info(
                                f"wheel: unable to replace {wantedkey} with {wheelkey}",
                            )
        nplayer += 1

    # reconfigure wheel min/max/deadzone
    procs = []
    recomputeSdlIds = False
    newPads = []
    for playercontroller, pad in sorted(players_controllers.items()):
        if (
            pad.dev in device_list
            and device_list[pad.dev]["isWheel"]
            and "wheel_rotation" in device_list[pad.dev]
        ):
            ra = int(device_list[pad.dev]["wheel_rotation"])
            wanted_ra = ra
            wanted_deadzone = 0
            wanted_midzone = 0

            # initialize values with games metadata
            if "wheel_rotation" in metadata:
                wanted_ra = int(metadata["wheel_rotation"])
            if "wheel_deadzone" in metadata:
                wanted_deadzone = int(metadata["wheel_deadzone"])
            if "wheel_midzone" in metadata:
                wanted_midzone = int(metadata["wheel_midzone"])

            # override with user configs
            if "wheel_rotation" in system.config:
                wanted_ra = int(system.config["wheel_rotation"])
            if "wheel_deadzone" in system.config:
                wanted_deadzone = int(system.config["wheel_deadzone"])
            if "wheel_midzone" in system.config:
                wanted_midzone = int(system.config["wheel_midzone"])

            eslog.info(
                "wheel rotation angle is "
                + str(ra)
                + " ; wanted wheel rotation angle is "
                + str(wanted_ra)
                + " ; wanted deadzone is "
                + str(wanted_deadzone)
                + " ; wanted midzone is "
                + str(wanted_midzone),
            )
            # no need new device in some cases
            if wanted_ra < ra or wanted_deadzone > 0:
                (newdev, p) = reconfigure_angle_rotation(
                    pad.dev,
                    int(pad.inputs["joystick1left"].id),
                    ra,
                    wanted_ra,
                    wanted_deadzone,
                    wanted_midzone,
                )
                if newdev is not None:
                    dev_match = match(r"^/dev/input/event([0-9]*)$", newdev)
                    if dev_match:
                        eslog.info(
                            f"replacing device {pad.dev} by device {newdev} for player {playercontroller}",
                        )
                        device_list[newdev] = dict(device_list[pad.dev])
                        device_list[newdev]["eventId"] = int(dev_match.group(1))
                        pad.physdev = pad.dev  # save the physical device for ffb
                        pad.dev = newdev  # needs to recompute sdl ids
                        recomputeSdlIds = True
                        newPads.append(newdev)
                        procs.append(p)
                    else:
                        eslog.warning(
                            f"Unexpected device name from wheel calibrator: {newdev}. Killing process.",
                        )
                        if p is not None:
                            kill(p.pid, SIGTERM)
                            p.communicate()

    # recompute sdl ids
    if recomputeSdlIds:
        # build the new joystick list
        joysticks = {}
        for node in device_list:
            if device_list[node]["isJoystick"]:
                joysticks[device_list[node]["eventId"]] = {"node": node}
        # add the new devices
        for p in newPads:
            matches = match(r"^/dev/input/event([0-9]*)$", str(p))
            if matches is not None:
                joysticks[int(matches.group(1))] = {"node": p}
        # find new sdl numeration
        joysticksByDev = {}
        for currentId, (_, x) in enumerate(sorted(joysticks.items())):
            joysticksByDev[x["node"]] = currentId
        # renumeration
        for _, pad in sorted(players_controllers.items()):
            if pad.dev in joysticksByDev:
                pad.index = joysticksByDev[pad.dev]
                device_list[pad.dev]["joystick_index"] = joysticksByDev[pad.dev]
        # fill physid
        for _, pad in sorted(players_controllers.items()):
            if (
                hasattr(pad, "physdev")
                and pad.physdev in device_list
                and "joystick_index" in device_list[pad.physdev]
            ):
                pad.physid = device_list[pad.physdev][
                    "joystick_index"
                ]  # save the physical device for ffb

    # reorder players to priorize wheel pads
    players_controllers_new = {}
    nplayer = 1
    for _, pad in sorted(players_controllers.items()):
        if (
            pad.dev in device_list and device_list[pad.dev]["isWheel"]
        ) or pad.dev in newPads:
            pad.player = str(nplayer)
            players_controllers_new[str(nplayer)] = pad
            nplayer += 1
    for _, pad in sorted(players_controllers.items()):
        if not (
            (pad.dev in device_list and device_list[pad.dev]["isWheel"])
            or pad.dev in newPads
        ):
            pad.player = str(nplayer)
            players_controllers_new[str(nplayer)] = pad
            nplayer += 1

    eslog.info("after wheel reconfiguration :")
    for playercontroller, pad in sorted(players_controllers_new.items()):
        eslog.info(
            "  "
            + playercontroller
            + ". index:"
            + str(pad.index)
            + " dev:"
            + pad.dev
            + " name:"
            + pad.name,
        )

    return (procs, players_controllers_new, device_list)


def get_wheels_from_device_infos(device_infos: dict[str, Any]) -> dict[str, Any]:
    res = {}
    for x in device_infos:
        # Check if device_infos[x] is a dictionary before accessing the key
        device_info = device_infos[x]
        if isinstance(device_info, dict) and device_info.get("isWheel"):
            res[x] = device_info
    return res


def reconfigure_angle_rotation(
    dev: Any,
    wheelAxis: int | str,
    rotationAngle: Any,
    wantedRotationAngle: Any,
    wantedDeadzone: Any,
    wantedMidzone: Any,
) -> tuple[str | None, Any]:
    devInfos = device.InputDevice(dev)
    caps = devInfos.capabilities()

    absmin = None
    absmax = None
    for item in caps.get(ecodes.EV_ABS, []):
        if isinstance(item, tuple) and len(item) == 2:
            v, absinfo = item
            if v == wheelAxis:
                absmin = absinfo.min
                absmax = absinfo.max

    if absmin is None or absmax is None:
        eslog.warning("unable to get min/max of " + dev)
        return (None, None)

    totalRange = absmax - absmin
    newmin = absmin
    newmax = absmax
    if wantedRotationAngle < rotationAngle:
        newRange = floor(totalRange * wantedRotationAngle / rotationAngle)
        newmin = absmin + ceil((totalRange - newRange) / 2)
        newmax = absmax - floor((totalRange - newRange) / 2)

    newdz = 0
    if wantedDeadzone > 0 and wantedDeadzone > wantedMidzone:
        newdz = floor(totalRange * wantedDeadzone / rotationAngle)
        newmin -= newdz // 2
        newmax += newdz // 2

    newmz = 0
    if wantedMidzone > 0:
        newmz = floor(totalRange * wantedMidzone / rotationAngle)
        newmin += newmz // 2
        newmax -= newmz // 2

    pipeout, pipein = pipe()
    cmd = [
        "batocera-wheel-calibrator",
        "-d",
        dev,
        "-a",
        str(wheelAxis),
        "-m",
        str(newmin),
        "-M",
        str(newmax),
        "-z",
        str(newdz),
        "-c",
        str(newmz),
    ]
    eslog.info(cmd)
    proc = Popen(cmd, stdout=pipein, stderr=PIPE)
    try:
        fd = fdopen(pipeout)
        newdev = fd.readline().rstrip("\n")
        fd.close()
    except OSError as e:
        eslog.error(f"Error reading from pipe: {e!s}")
        kill(proc.pid, SIGTERM)
        proc.communicate()
        raise

    return (newdev, proc)


def reset_controllers(wheel_processes: Any) -> None:
    for p in wheel_processes:
        eslog.info(f"killing wheel process {p.pid}")
        kill(p.pid, SIGTERM)
        p.communicate()
