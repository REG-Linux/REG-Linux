#!/usr/bin/env python

import os

from utils.logger import get_logger
eslog = get_logger(__name__)


sway_launched = False
weston_launched = False
gamescope_launched = False

# TODO implement start_weston
def start_weston(generator, system):
    global weston_launched
    if not weston_launched:
        weston_launched = True

# TODO implement stop_weston
def stop_weston(generator, system):
    global weston_launched
    if weston_launched:
        weston_launched = False

def start_sway(generator, system):
    global sway_launched
    if not sway_launched:
        os.system("WLR_LIBINPUT_NO_DEVICES=1 /usr/bin/sway -c /etc/sway/launchconfig -d & > /userdata/system/logs/sway.log 2>&1")
        os.environ["WAYLAND_DISPLAY"]="wayland-1"
        os.environ["XDG_RUNTIME_DIR"]="/var/run"
        os.environ["SWAYSOCK"]="/var/run/sway-ipc.0.sock"
        os.environ["SDL_VIDEODRIVER"]="wayland"
        sway_launched = True
        eslog.debug("Composer started!")

def stop_sway(generator, system):
    global sway_launched
    if sway_launched:
        os.system("swaymsg exit")
        del os.environ["WAYLAND_DISPLAY"]
        del os.environ["XDG_RUNTIME_DIR"]
        del os.environ["SWAYSOCK"]
        del os.environ["SDL_VIDEODRIVER"]
        sway_launched = False
        eslog.debug("Composer finished!")

# TODO handle gamescope
def start_compositor(generator, system):
    # If Weston is present, we should use it
    if os.path.exists("/usr/bin/weston"):
        start_weston(generator, system)
        return

    # Fallback on Sway (default case)
    if os.path.exists("/usr/bin/sway"):
        start_sway(generator, system)
        return

# TODO handle gamescope
def stop_compositor(generator, system):
    # Stop sway if launched
    if sway_launched:
        stop_sway(generator, system)
        return

    # Stop weston if launched
    if weston_launched:
        stop_weston(generator, system)
        return
