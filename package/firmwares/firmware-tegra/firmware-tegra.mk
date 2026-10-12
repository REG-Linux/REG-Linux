################################################################################
#
# firmware-tegra
#
################################################################################

FIRMWARE_TEGRA_VERSION = 0.0.1
FIRMWARE_TEGRA_SOURCE =
FIRMWARE_TEGRA_DEPENDENCIES += alllinuxfirmwares

define FIRMWARE_TEGRA_INSTALL_TARGET_CMDS
	# Ensure Tegra/Nouveau firmware is available
	# The nvidia/gm20b and tegra210 firmware is included in alllinuxfirmwares
	mkdir -p $(TARGET_DIR)/lib/firmware/nvidia/tegra210
	mkdir -p $(TARGET_DIR)/lib/firmware/nvidia/gm20b
endef

$(eval $(generic-package))
