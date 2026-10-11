#!/bin/dash

# XDG_RUNTIME_DIR must be 0700 and owned by the user. /var/run is shared 0755
# root, which Wayland clients warn or abort against, so use /run/user/<uid>.
_uid=$(id -u)
export XDG_RUNTIME_DIR="/run/user/${_uid}"
mkdir -p "$XDG_RUNTIME_DIR" 2>/dev/null
chmod 0700 "$XDG_RUNTIME_DIR" 2>/dev/null
chown "$_uid:$(id -g)" "$XDG_RUNTIME_DIR" 2>/dev/null
unset _uid

export XDG_CONFIG_HOME=/userdata/system/configs \
       XDG_CACHE_HOME=/userdata/system/cache \
       XDG_DATA_HOME=/userdata/saves

# Set SDL game controller config file path based on user override
if [ -e /userdata/system/configs/regstation/gamecontrollerdb.txt ]; then
    export SDL_GAMECONTROLLERCONFIG_FILE=/userdata/system/configs/regstation/gamecontrollerdb.txt
else
    export SDL_GAMECONTROLLERCONFIG_FILE=/usr/share/regstation/gamecontrollerdb.txt
fi

# Graphical environment (system.rs.environment). An explicit choice wins; when
# unset, auto-detect Wayland for stacks that cannot drive bare KMSDRM.
case "$(/usr/bin/regmsg systemconf getconfigkey system.rs.environment)" in
    wayland)
        export XDG_SESSION_TYPE=wayland \
               SDL_VIDEO_DRIVER=wayland \
               QT_QPA_PLATFORM=wayland
        ;;
    drm)
        export XDG_SESSION_TYPE=drm \
               QT_QPA_PLATFORM=xcb \
               LD_PRELOAD=/usr/lib/libdrmhook.so
        [ -e /dev/dri/card0 ] && export SDL_VIDEO_DRIVER=kmsdrm
        ;;
    *)
        # Stacks that mandate Wayland: virtio-gpu (KMSDRM pageflip fails
        # EINVAL) and the libmali blob (Vulkan WSI is wayland-only, and its
        # GBM path expects a wlroots/weston-managed surface).
        _needs_wayland=0
        if [ -d /sys/bus/virtio/drivers/virtio_gpu ] && \
           ls /sys/bus/virtio/drivers/virtio_gpu/virtio* >/dev/null 2>&1; then
            _needs_wayland=1
        fi
        if ls /usr/lib/libMaliVulkan.so* >/dev/null 2>&1 || \
           ls /usr/lib/libmali-valhall-* >/dev/null 2>&1; then
            _needs_wayland=1
        fi

        if [ "$_needs_wayland" = 1 ]; then
            export XDG_SESSION_TYPE=wayland \
                   SDL_VIDEO_DRIVER=wayland \
                   QT_QPA_PLATFORM=wayland
        else
            export XDG_SESSION_TYPE=drm \
                   QT_QPA_PLATFORM=xcb \
                   LD_PRELOAD=/usr/lib/libdrmhook.so
            # SDL3 does not infer KMSDRM from XDG_SESSION_TYPE=drm
            [ -e /dev/dri/card0 ] && export SDL_VIDEO_DRIVER=kmsdrm
        fi
        unset _needs_wayland
        ;;
esac

# Graphics API (global.gfxbackend): "gl" / "glcore" / "vulkan", unset = decided
# by the capability ladder in regmsg's lib/libretro/config.lua. This is the one
# key for the whole stack -- the compositor and the frontend here, RetroArch's
# video_driver, and the standalone emulators' own backend defaults -- so a board
# or a user states the preference once instead of per component.
# Only "vulkan" is acted on. Everything else means GL: wlroots has no separate
# glcore renderer, and the distinction only reaches as far as RetroArch, which
# reads the same key through its own generator.
#
# REG-Station is told through REGSTATION_RENDER_DRIVER, not SDL_RENDER_DRIVER:
# emulators inherit this environment, and SDL2 has no vulkan SDL_Renderer at all.
if [ "$(/usr/bin/regmsg systemconf getconfigkey global.gfxbackend)" = "vulkan" ]; then
    export REGSTATION_RENDER_DRIVER=vulkan \
           WLR_RENDERER=vulkan

    # wlroots hands the renderer the backend's KMS node, so where display and
    # render are separate devices (C5: meson KMS + panthor GPU) the Vulkan
    # renderer matches no physical device and sway exits. GLES2 is immune via
    # Mesa's kmsro. Point it at the render node of the DRM device exposing no
    # connectors, i.e. the GPU; where one device does both, none matches and
    # the variable stays unset, which is correct.
    for _r in /dev/dri/renderD*; do
        [ -e "$_r" ] || continue
        _sys="/sys/class/drm/$(basename "$_r")/device"
        if ! ls -d "$_sys"/drm/card*/card*-* >/dev/null 2>&1; then
            export WLR_RENDER_DRM_DEVICE="$_r"
            break
        fi
    done
    unset _r _sys
fi
