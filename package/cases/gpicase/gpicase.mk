################################################################################
#
# gpicase
#
################################################################################
GPICASE_VERSION = 0.2
GPICASE_SOURCE =
GPICASE_DEPENDENCIES = linux
BR2_EXTERNAL_GPICASE_PATH=$(BR2_EXTERNAL_REGLINUX_PATH)/package/cases/gpicase

define GPICASE_BUILD_CMDS
	$(HOST_DIR)/bin/linux-dtc $(BR2_EXTERNAL_GPICASE_PATH)/overlays/retroflag-gpicase-overlay.dts -o	$(@D)/retroflag-gpicase.dtbo
	$(HOST_DIR)/bin/linux-dtc $(BR2_EXTERNAL_GPICASE_PATH)/overlays/retroflag-gpicase2-overlay.dts -o	$(@D)/retroflag-gpicase2.dtbo
	$(HOST_DIR)/bin/linux-dtc $(BR2_EXTERNAL_GPICASE_PATH)/overlays/retroflag-gpicase2w-overlay.dts -o	$(@D)/retroflag-gpicase2w.dtbo
endef

define GPICASE_INSTALL_TARGET_CMDS
	mkdir -p $(BINARIES_DIR)/rpi-firmware/overlays
	$(INSTALL) -m 0755 $(@D)/*.dtbo	$(BINARIES_DIR)/rpi-firmware/overlays/
	$(INSTALL) -m 0755 $(BR2_EXTERNAL_GPICASE_PATH)/scripts/gpicase-install	$(TARGET_DIR)/usr/bin/gpicase-install
endef

$(eval $(generic-package))
