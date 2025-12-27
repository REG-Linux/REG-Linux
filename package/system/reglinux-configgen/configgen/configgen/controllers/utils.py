import re
from pathlib import Path
from typing import Any


def shortNameFromPath(path_name: str) -> str:
    redname = Path(path_name).stem.lower()
    inpar = False
    inblock = False
    ret = ""
    for c in redname:
        if (
            not inpar
            and not inblock
            and ((c >= "a" and c <= "z") or (c >= "0" and c <= "9"))
        ):
            ret += c
        elif c == "(":
            inpar = True
        elif c == ")":
            inpar = False
        elif c == "[" or c == "]":
            inblock = True
    return ret


def dev2int(dev: str) -> Any:
    matches = re.match(r"^/dev/input/event([0-9]*)$", dev)
    if matches is None:
        return None
    return int(matches.group(1))
