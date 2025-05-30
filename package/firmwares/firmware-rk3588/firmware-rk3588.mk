################################################################################
#
# firmware-rk3588
#
################################################################################

FIRMWARE_RK3588_VERSION = 0.0.1
FIRMWARE_RK3588_SOURCE =
FIRMWARE_RK3588_DEPENDENCIES += alllinuxfirmwares
FIRMWARE_RK3588_DEPENDENCIES += firmware-radxa-rkwifibt

FIRMWARE_RK3588_PATH = $(BR2_EXTERNAL_REGLINUX_PATH)/package/firmwares/firmware-rk3588
FIRMWARE_RK3588_TARGET_DIR=$(TARGET_DIR)/lib/firmware

define FIRMWARE_RK3588_INSTALL_TARGET_CMDS
	cp -prv $(FIRMWARE_RK3588_PATH)/firmware/* $(TARGET_DIR)/lib/firmware/
endef

$(eval $(generic-package))
