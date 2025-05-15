################################################################################
#
# xpad-noone
#
################################################################################
# Version: Commits on Jan 10, 2024
XPAD_NOONE_VERSION = 96d119aabacb84d39ed9c95ae48cc4891496ccb4
XPAD_NOONE_SITE = $(call github,medusalix,xpad-noone,$(XPAD_NOONE_VERSION))
XPAD_NOONE_DEPENDENCIES = host-cabextract libusb
XPAD_NOONE_PATH = $(BR2_EXTERNAL_REGLINUX_PATH)/package/controllers/pads/xpad-noone

XPAD_NOONE_USER_EXTRA_CFLAGS = -w -Wno-error=unused-function

XPAD_NOONE_MODULE_MAKE_OPTS = \
	KCFLAGS="$$KCFLAGS $(XPAD_NOONE_USER_EXTRA_CFLAGS)"

define XPAD_NOONE_MODPROBE_CMD
	$(INSTALL) -D -m 0644 $(XPAD_NOONE_PATH)/xpad_noone.conf $(TARGET_DIR)/etc/modprobe.d/xpad_noone.conf
endef

XPAD_NOONE_POST_INSTALL_TARGET_HOOKS += XPAD_NOONE_MODPROBE_CMD

$(eval $(kernel-module))
$(eval $(generic-package))
