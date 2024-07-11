################################################################################
#
# uboot files for Tinkerboard 2
#
################################################################################

UBOOT_TINKERBOARD2_VERSION = 2024.07.09
UBOOT_TINKERBOARD2_SOURCE =

define UBOOT_TINKERBOARD2_BUILD_CMDS
endef

define UBOOT_TINKERBOARD2_INSTALL_TARGET_CMDS
	mkdir -p $(BINARIES_DIR)/uboot-tinkerboard2
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/reglinux/boot/uboot-tinkerboard2/idbloader.img $(BINARIES_DIR)/uboot-tinkerboard2/idbloader.img
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/reglinux/boot/uboot-tinkerboard2/u-boot.itb $(BINARIES_DIR)/uboot-tinkerboard2/u-boot.itb
endef

$(eval $(generic-package))
