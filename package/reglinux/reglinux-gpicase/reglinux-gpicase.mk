################################################################################
#
# gpicase
#
################################################################################
REGLINUX_GPICASE_VERSION = 0.1
REGLINUX_GPICASE_SOURCE =

define REGLINUX_GPICASE_BUILD_CMDS
	$(HOST_DIR)/bin/linux-dtc $(BR2_EXTERNAL_BATOCERA_PATH)/package/reglinux/reglinux-gpicase/overlays/retroflag-gpicase-overlay.dts -o	$(@D)/retroflag-gpicase.dtbo
	$(HOST_DIR)/bin/linux-dtc $(BR2_EXTERNAL_BATOCERA_PATH)/package/reglinux/reglinux-gpicase/overlays/retroflag-gpicase2-overlay.dts -o	$(@D)/retroflag-gpicase2.dtbo
	$(HOST_DIR)/bin/linux-dtc $(BR2_EXTERNAL_BATOCERA_PATH)/package/reglinux/reglinux-gpicase/overlays/retroflag-gpicase2w-overlay.dts -o	$(@D)/retroflag-gpicase2w.dtbo
endef

define REGLINUX_GPICASE_INSTALL_TARGET_CMDS
	mkdir -p $(BINARIES_DIR)/rpi-firmware/overlays
	install -m 0755 $(@D)/*.dtbo	$(BINARIES_DIR)/rpi-firmware/overlays/

	install -m 0755 $(BR2_EXTERNAL_BATOCERA_PATH)/package/reglinux/reglinux-gpicase/scripts/99-gpicase.rules		$(TARGET_DIR)/etc/udev/rules.d/
	install -m 0755 $(BR2_EXTERNAL_BATOCERA_PATH)/package/reglinux/reglinux-gpicase/scripts/reglinux-gpicase-install	$(TARGET_DIR)/usr/bin/reglinux-gpicase-install
endef

$(eval $(generic-package))
