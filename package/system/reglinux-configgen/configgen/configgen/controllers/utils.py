from os import path
import re

def shortNameFromPath(path_name):
    redname = path.splitext(path.basename(path_name))[0].lower()
    inpar   = False
    inblock = False
    ret = ""
    for c in redname:
        if not inpar and not inblock and ( (c >= 'a' and c <= 'z') or (c >= '0' and c <= '9') ):
            ret += c
        elif c == '(':
            inpar = True
        elif c == ')':
            inpar = False
        elif c == '[':
            inblock = True
        elif c == ']':
            inblock = True
    return ret

def dev2int(dev):
    matches = re.match(r"^/dev/input/event([0-9]*)$", dev)
    if matches is None:
        return None
    return int(matches.group(1))
