################################################################################
#
# zramswap
#
################################################################################

ZRAMSWAP_VERSION = 0.0.1
ZRAMSWAP_SOURCE =
ZRAMSWAP_SITE =

define ZRAMSWAP_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/usr/share/reglinux/services
	$(INSTALL) -Dm755 $(BR2_EXTERNAL_BATOCERA_PATH)/package/utils/zramswap/zramswap $(TARGET_DIR)/usr/share/reglinux/services/
endef

$(eval $(generic-package))
