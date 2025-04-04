################################################################################
#
# regmsg
#
################################################################################

REGLINUX_MSG_VERSION = 0.0.2
REGLINUX_MSG_SITE = $(call github,jdorigao,regmsg,$(REGLINUX_MSG_VERSION))
REGLINUX_MSG_LICENSE = MIT
REGLINUX_MSG_LICENSE_FILES = LICENSE

REGLINUX_MSG_LOCATION = target/$(RUSTC_TARGET_NAME)/$(if $(BR2_ENABLE_DEBUG),debug,release)

define REGLINUX_MSG_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/$(REGLINUX_MSG_LOCATION)/regmsg	$(TARGET_DIR)/usr/bin/
	ln -sf regmsg $(TARGET_DIR)/usr/bin/system-resolution
endef

$(eval $(rust-package))
