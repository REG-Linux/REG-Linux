################################################################################
#
# xwiimote
#
################################################################################

XWIIMOTE_VERSION = v3.0.1
XWIIMOTE_SITE = $(call github,dev-0x7C6,xwiimote-ng,$(XWIIMOTE_VERSION))
XWIIMOTE_LICENSE = GPL-2.0+
XWIIMOTE_LICENSE_FILES = COPYING

# udev is needed for per-package build isolation
XWIIMOTE_DEPENDENCIES = ncurses udev

$(eval $(cmake-package))
