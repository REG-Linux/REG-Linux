################################################################################
#
# BATOCERA ETHTOOL
#
################################################################################

define BATOCERA_ETHTOOL_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/etc/udev/rules.d
	cp $(BR2_EXTERNAL_REGLINUX_PATH)/package/batocera/utils/batocera-ethtool/99-wol.rules $(TARGET_DIR)/etc/udev/rules.d
endef

$(eval $(generic-package))
