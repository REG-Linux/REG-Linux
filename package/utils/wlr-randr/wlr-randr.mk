################################################################################
#
# wlr-randr
#
################################################################################

# Release 0.5.0 on - Feb 12, 2025
WLR_RANDR_VERSION = 0.5.0
WLR_RANDR_SITE = https://gitlab.freedesktop.org/emersion/wlr-randr/-/releases/v$(WAYLAND_VERSION)/downloads
WLR_RANDR_SOURCE = wlr-randr-$(WLR_RANDR_VERSION).tar.gz
WLR_RANDR_LICENSE = MIT
WLR_RANDR_LICENSE_FILES = LICENSE

$(eval $(meson-package))
