################################################################################
#
# regmsg
#
################################################################################

# Nov 13, 2025
REGLINUX_MSG_VERSION = aecee169bf43a12cd6aef67d7f5a173a6e2035e4
REGLINUX_MSG_TOKEN = $(shell cat /build/gh_token)
REGLINUX_MSG_SITE = https://$(REGLINUX_MSG_TOKEN)@github.com/REG-Linux/regmsg
REGLINUX_MSG_SITE_METHOD = git
REGLINUX_MSG_LICENSE = MIT
REGLINUX_MSG_LICENSE_FILES = LICENSE
REGLINUX_MSG_DEPENDENCIES += libdrm

RUSTC_TARGET_PROFILE = $(if $(BR2_ENABLE_DEBUG),debug,release)
REGLINUX_MSG_LOCATION = target/$(RUSTC_TARGET_NAME)/$(RUSTC_TARGET_PROFILE)

define REGLINUX_MSG_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/$(REGLINUX_MSG_LOCATION)/regmsg			$(TARGET_DIR)/usr/bin/
	$(INSTALL) -D $(@D)/$(REGLINUX_MSG_LOCATION)/regmsgd			$(TARGET_DIR)/usr/bin/
	$(INSTALL) -D $(@D)/$(REGLINUX_MSG_LOCATION)/regmsg_shell		$(TARGET_DIR)/usr/bin/
	$(INSTALL) -D $(@D)/target/$(RUSTC_TARGET_PROFILE)/libdrmhook.so	$(TARGET_DIR)/usr/lib/
	$(INSTALL) -D $(@D)/target/$(RUSTC_TARGET_PROFILE)/S06regmsgd		$(TARGET_DIR)/etc/init.d/
endef

$(eval $(cargo-package))
