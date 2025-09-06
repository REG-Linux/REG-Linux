################################################################################
#
# xwiimote
#
################################################################################

XWIIMOTE_VERSION = v3.0.1
XWIIMOTE_SITE = $(call github,dev-0x7C6,xwiimote-ng,$(XWIIMOTE_VERSION))

XWIIMOTE_DEPENDENCIES = udev ncurses

$(eval $(cmake-package))
