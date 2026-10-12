#!/usr/bin/env python3
# Distills a full MAME "-listxml" release dump down to just the fields
# regmsgd's library::arcade needs (name/isbios/isdevice/runnable,
# description, year, manufacturer, display rotation, input players,
# control types), dropping ROM lists, DIP switches, device refs, etc.
# that make up the bulk of the ~300MB+ original. Keeps the same
# element/attribute shapes as upstream -listxml (just a subset of them,
# and de-duplicated control types instead of one per player) so it
# parses with regmsgd's existing parse_listxml, unchanged, exactly as if
# it were reading a live "mame -listxml" run.
import sys
import xml.etree.ElementTree as ET
from xml.sax.saxutils import escape, quoteattr


def strip(src_path, dst_path):
    with open(dst_path, "w", encoding="utf-8") as out:
        out.write('<?xml version="1.0"?>\n<mame>\n')
        for _, elem in ET.iterparse(src_path, events=("end",)):
            if elem.tag != "machine":
                continue
            name = elem.get("name", "")
            isbios = elem.get("isbios", "no")
            isdevice = elem.get("isdevice", "no")
            runnable = elem.get("runnable", "yes")
            description = elem.findtext("description", "")
            year = elem.findtext("year", "")
            manufacturer = elem.findtext("manufacturer", "")
            display = elem.find("display")
            rotate = display.get("rotate", "") if display is not None else ""
            inp = elem.find("input")
            players = inp.get("players", "") if inp is not None else ""
            # De-duplicated, order-preserving (one <control> per player in
            # the source repeats the same type - input_device() only cares
            # whether a type is present at all, not how many times).
            control_types = []
            if inp is not None:
                for c in inp.findall("control"):
                    t = c.get("type", "")
                    if t and t not in control_types:
                        control_types.append(t)

            out.write(
                "\t<machine name=%s isbios=%s isdevice=%s runnable=%s>\n"
                % (
                    quoteattr(name),
                    quoteattr(isbios),
                    quoteattr(isdevice),
                    quoteattr(runnable),
                )
            )
            out.write("\t\t<description>%s</description>\n" % escape(description))
            if year:
                out.write("\t\t<year>%s</year>\n" % escape(year))
            if manufacturer:
                out.write("\t\t<manufacturer>%s</manufacturer>\n" % escape(manufacturer))
            if rotate:
                out.write('\t\t<display rotate=%s/>\n' % quoteattr(rotate))
            if players or control_types:
                out.write('\t\t<input players=%s>\n' % quoteattr(players))
                for t in control_types:
                    out.write('\t\t\t<control type=%s/>\n' % quoteattr(t))
                out.write("\t\t</input>\n")
            out.write("\t</machine>\n")

            elem.clear()
        out.write("</mame>\n")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.stderr.write("usage: strip-mame-xml.py <src.xml> <dst.xml>\n")
        sys.exit(1)
    strip(sys.argv[1], sys.argv[2])
