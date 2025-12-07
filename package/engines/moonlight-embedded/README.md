# moonlight-embedded

Moonlight-embedded is the open-source GameStream client for embedded Linux targets.

## Configuration
- **Version:** v2.7.1 from `irtimmer/moonlight-embedded` with git submodules.
- **Config selections:** pulls in opus, expat, libevdev, Avahi, ALSA, udev support, libcurl, libcec, FFmpeg (including swscale), SDL2, libenet, and optionally VA Intel drivers when building on x86.
- **Build system:** CMake with `-DCMAKE_INSTALL_SYSCONFDIR=/etc`. Enables X11 only when `BR2_PACKAGE_XORG7` is enabled and bundles optional VA/Intel drivers for Intel targets.

## Extras
- Applies `002-include-drm_fourcc.patch` to keep the DRM userland headers in sync with the desktop dependencies.
- Installs `moonlight.conf` plus a helper `system-moonlight` launcher on the target and copies `moonlight.moonlight.keys` into `/usr/share/evmapy`.
