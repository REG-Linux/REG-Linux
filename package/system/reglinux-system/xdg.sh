#!/bin/sh

export XDG_RUNTIME_DIR=/var/run
export XDG_CONFIG_HOME=/userdata/system/configs
export XDG_CACHE_HOME=/userdata/system/cache
export XDG_DATA_HOME=/userdata/saves


environment="$(/usr/bin/system-settings-get-master system.es.environment)"

if [ "$environment" = "wayland" ]; then
	export XDG_SESSION_TYPE=wayland
	export SDL_VIDEO_DRIVER=wayland
	export QT_QPA_PLATFORM=wayland
else
	export XDG_SESSION_TYPE=drm
	export QT_QPA_PLATFORM=xcb
    export LD_PRELOAD=/usr/lib/libdrmhook.so
fi
