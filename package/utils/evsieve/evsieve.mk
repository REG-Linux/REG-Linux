################################################################################
#
# evsieve
#
################################################################################

EVSIEVE_VERSION = v1.4.0
EVSIEVE_SOURCE = foo-$(EVSIEVE_VERSION).tar.gz
EVSIEVE_SITE = $(call github,KarsMulder,evsieve,$(EVSIEVE_VERSION))
EVSIEVE_LICENSE = GPLv2
EVSIEVE_LICENSE_FILES = COPYING

EVSIEVE_DEPENDENCIES = libevdev

EVSIEVE_CARGO_INSTALL_OPTS = --path ./

define EVISEVE_STRIP_BINARY
	$(TARGET_STRIP) $(TARGET_DIR)/usr/bin/evsieve
endef

define EVSIEVE_POST_INSTALL_CMDS
	$(INSTALL) -D -m 0755 $(BR2_EXTERNAL_REGLINUX_PATH)/package/utils/evsieve/evsieve-merge-devices \
 		$(TARGET_DIR)/usr/bin/evsieve-merge-devices
	$(TARGET_STRIP) -s $(TARGET_DIR)/usr/bin/evsieve
	$(INSTALL) -D -m 0755 $(BR2_EXTERNAL_REGLINUX_PATH)/package/utils/evsieve/evsieve-helper $(TARGET_DIR)/usr/bin/evsieve-helper
endef

EVSIEVE_POST_INSTALL_TARGET_HOOKS += EVSIEVE_STRIP_BINARY
EVSIEVE_POST_INSTALL_TARGET_HOOKS += EVSIEVE_POST_INSTALL_CMDS

$(eval $(rust-package))
