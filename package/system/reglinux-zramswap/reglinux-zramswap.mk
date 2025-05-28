################################################################################
#
# zramswap
#
################################################################################

REGLINUX_ZRAMSWAP_VERSION = 0.1.0
REGLINUX_ZRAMSWAP_SOURCE =
REGLINUX_ZRAMSWAP_SITE =

define REGLINUX_ZRAMSWAP_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/usr/share/reglinux/services
	$(INSTALL) -Dm755 $(BR2_EXTERNAL_REGLINUX_PATH)/package/system/reglinux-zramswap/zramswap $(TARGET_DIR)/usr/share/reglinux/services/
endef

$(eval $(generic-package))
