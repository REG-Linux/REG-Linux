#!/bin/bash

GADGET_MARKER="/var/run/reglinux-game.running"

case "$1" in
    gameStart)
        touch "${GADGET_MARKER}"
        if [ -x /usr/bin/usbgadget ]; then
            /usr/bin/usbgadget stop
        fi
        ;;
    gameStop)
        rm -f "${GADGET_MARKER}"
        if [ -x /usr/bin/usbgadget ]; then
            /usr/bin/usbgadget --start
        fi
        ;;
    *)
        exit 0
        ;;
esac

exit 0
