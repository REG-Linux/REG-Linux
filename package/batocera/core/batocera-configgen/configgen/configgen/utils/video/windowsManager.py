#!/usr/bin/env python

import os

from utils.logger import get_logger
eslog = get_logger(__name__)

sway_launched = False
gamescope_launched = False

def start_sway(generator, system):
    global sway_launched
    if not sway_launched:
        os.system("WLR_LIBINPUT_NO_DEVICES=1 /usr/bin/sway -c /etc/sway/launchconfig &")
        os.environ["WAYLAND_DISPLAY"]="wayland-1"
        os.environ["XDG_RUNTIME_DIR"]="/var/run"
        os.environ["SWAYSOCK"]="/var/run/sway-ipc.0.sock"
        os.environ["SDL_VIDEODRIVER"]="wayland"
        os.environ["XDG_SESSION_TYPE"]="wayland"
        os.environ["QT_QPA_PLATFORM"]="wayland"
        if generator.requiresX11():
            os.environ["DISPLAY"]=":0"
            os.environ["QT_QPA_PLATFORM"]="xcb"
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
        os.environ["XDG_SESSION_TYPE"]="drm"
        os.environ["QT_QPA_PLATFORM"]="xcb"
        if generator.requiresX11():
            del os.environ["DISPLAY"]
        sway_launched = False
        eslog.debug("Composer finished!")

# TODO handle gamescope
def start_compositor(generator, system):
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
