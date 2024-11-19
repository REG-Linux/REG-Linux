#!/bin/sh

if [ $(pgrep -x sway) ]; then
    export WAYLAND_DISPLAY=wayland-1
    export XDG_RUNTIME_DIR=/var/run
    export SWAYSOCK=/var/run/sway-ipc.0.sock
fi
