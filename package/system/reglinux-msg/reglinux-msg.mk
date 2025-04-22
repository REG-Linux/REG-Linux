################################################################################
#
# regmsg
#
################################################################################

REGLINUX_MSG_VERSION = 1080dcf9b8bfe5f15e33d5e31fb57b5fc9ac3555
REGLINUX_MSG_SITE = $(call github,jdorigao,regmsg,$(REGLINUX_MSG_VERSION))
REGLINUX_MSG_LICENSE = MIT
REGLINUX_MSG_LICENSE_FILES = LICENSE

REGLINUX_MSG_DEPENDENCIES += libdrm

RUSTC_TARGET_PROFILE = $(if $(BR2_ENABLE_DEBUG),debug,release)
REGLINUX_MSG_LOCATION = target/$(RUSTC_TARGET_NAME)/$(RUSTC_TARGET_PROFILE)

define REGLINUX_MSG_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/$(REGLINUX_MSG_LOCATION)/regmsg			$(TARGET_DIR)/usr/bin/
	$(INSTALL) -D $(@D)/target/$(RUSTC_TARGET_PROFILE)/libdrmhook.so	$(TARGET_DIR)/usr/lib/
	ln -sf regmsg $(TARGET_DIR)/usr/bin/system-resolution
endef

$(eval $(rust-package))
