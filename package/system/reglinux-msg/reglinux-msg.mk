################################################################################
#
# regmsg
#
################################################################################

REGLINUX_MSG_VERSION = d60a496a01400324041b62b38e0ed0a5dfad6971
REGLINUX_MSG_SITE = $(call github,rtissera,regmsg,$(REGLINUX_MSG_VERSION))
REGLINUX_MSG_LICENSE = MIT
REGLINUX_MSG_LICENSE_FILES = LICENSE

REGLINUX_MSG_DEPENDENCIES += libdrm

RUSTC_TARGET_PROFILE = $(if $(BR2_ENABLE_DEBUG),debug,release)
REGLINUX_MSG_LOCATION = target/$(RUSTC_TARGET_NAME)/$(RUSTC_TARGET_PROFILE)

REGLINUX_MSG_CARGO_BUILD_OPTS += --features cli,daemon

define REGLINUX_MSG_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/$(REGLINUX_MSG_LOCATION)/regmsg			$(TARGET_DIR)/usr/bin/
	$(INSTALL) -D $(@D)/$(REGLINUX_MSG_LOCATION)/regmsgd			$(TARGET_DIR)/usr/bin/
	$(INSTALL) -D $(@D)/target/$(RUSTC_TARGET_PROFILE)/libdrmhook.so	$(TARGET_DIR)/usr/lib/
	ln -sf regmsg $(TARGET_DIR)/usr/bin/system-resolution
endef

$(eval $(cargo-package))
