#!/usr/bin/env python3
# Extracts the Atari Lynx screen-rotation table from MAME's hash/lynx.xml
# softlist into the "title;angle" CSV regmsgd's launcher::helpers reads for
# alt_decoration.
#
# Why a generated table for lynx and hand-maintained ones for everything else:
# of MAME's 764 softlists, hash/lynx.xml is the ONLY one carrying rotation
# metadata (<feature name="rotation" value="LEFT|RIGHT"/>). wswan/wscolor and
# vectrex softlists have hardware descriptors only, nds/3ds have no MAME
# support at all, and no dat format (No-Intro, Redump, ClrMamePro) carries
# rotation. Arcade rotation is NOT here -- it comes from <display rotate> in
# mame-stripped.xml.gz, which this package already produces.
#
# Keys are normalised (lowercase, everything from the first "(" dropped)
# because MAME descriptions never match No-Intro filename stems verbatim:
# MAME says "Klax (Europe, USA)" where the ROM on disk is "Klax (USA, Europe)".
# helpers.rs normalises the ROM stem the same way for its second-pass lookup.
import sys
import xml.etree.ElementTree as ET

# MAME describes the physical cabinet rotation; regmsgd wants the angle to
# rotate the display BY, matching <display rotate> on the arcade side.
ANGLES = {"LEFT": "90", "RIGHT": "270"}


def normalize(title):
    return title.split("(")[0].strip().lower()


def generate(src_path, dst_path):
    rows = {}
    for _, elem in ET.iterparse(src_path, events=("end",)):
        if elem.tag != "software":
            continue
        for feature in elem.iter("feature"):
            if feature.get("name") != "rotation":
                continue
            angle = ANGLES.get((feature.get("value") or "").upper())
            title = normalize(elem.findtext("description", ""))
            if angle and title:
                rows[title] = angle
        elem.clear()

    with open(dst_path, "w", encoding="utf-8") as out:
        out.write("# Generated from MAME hash/lynx.xml -- do not edit.\n")
        out.write("# <normalised title>;<rotation angle>\n")
        for title in sorted(rows):
            out.write("%s;%s\n" % (title, rows[title]))
    return len(rows)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit("usage: lynx-rotation-csv.py <hash/lynx.xml> <lynx.csv>")
    count = generate(sys.argv[1], sys.argv[2])
    print("lynx-rotation-csv: %d rotated titles" % count)
    # A softlist that suddenly has no rotation features means the upstream
    # format changed; fail loudly rather than shipping an empty table.
    if count == 0:
        sys.exit("lynx-rotation-csv: no rotation features found in %s" % sys.argv[1])
