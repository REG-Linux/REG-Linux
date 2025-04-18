#!/bin/sh

if pgrep -x sway > /dev/null; then
    runtime_dir="/var/run"
    export WAYLAND_DISPLAY=wayland-1
    export XDG_RUNTIME_DIR="$runtime_dir"
    export SWAYSOCK="$runtime_dir/sway-ipc.0.sock"
fi
