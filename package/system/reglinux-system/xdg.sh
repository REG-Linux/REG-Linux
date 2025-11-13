#!/bin/dash

# Set XDG base directories
export XDG_RUNTIME_DIR=/var/run \
       XDG_CONFIG_HOME=/userdata/system/configs \
       XDG_CACHE_HOME=/userdata/system/cache \
       XDG_DATA_HOME=/userdata/saves

# Set SDL game controller config file path based on user override
if [ -e /userdata/system/configs/emulationstation/gamecontrollerdb.txt ]; then
    export SDL_GAMECONTROLLERCONFIG_FILE=/userdata/system/configs/emulationstation/gamecontrollerdb.txt
else
    export SDL_GAMECONTROLLERCONFIG_FILE=/usr/share/emulationstation/gamecontrollerdb.txt
fi

# Select graphical environment settings (Wayland or DRM)
case "$(/usr/bin/regmsg getConfigKey system.es.environment)" in
    wayland)
        # Configure environment for Wayland
        export XDG_SESSION_TYPE=wayland \
               SDL_VIDEO_DRIVER=wayland \
               QT_QPA_PLATFORM=wayland
        ;;
    *)
        # Configure environment for legacy DRM/GL or X11 fallback
        export XDG_SESSION_TYPE=drm \
               QT_QPA_PLATFORM=xcb \
               LD_PRELOAD=/usr/lib/libdrmhook.so
        ;;
esac
