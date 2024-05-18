################################################################################
#
# uboot files for BananaPi F3 (StarmiT K1)
#
################################################################################

UBOOT_BANANAPI_F3_VERSION = 1.0
UBOOT_BANANAPI_F3_SITE = 
UBOOT_BANANAPI_F3_SOURCE = 

define UBOOT_BANANAPI_F3_EXTRACT_CMDS
endef

define UBOOT_BANANAPI_F3_BUILD_CMDS
endef

define UBOOT_BANANAPI_F3_INSTALL_TARGET_CMDS
	mkdir -p $(BINARIES_DIR)/uboot-bananapi-f3
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/reglinux/boot/uboot-bananapi-f3/FSBL.bin $(BINARIES_DIR)/uboot-bananapi-f3/FSBL.bin
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/reglinux/boot/uboot-bananapi-f3/env.img  $(BINARIES_DIR)/uboot-bananapi-f3/env.img
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/reglinux/boot/uboot-bananapi-f3/fw_dynamic.itb $(BINARIES_DIR)/uboot-bananapi-f3/fw_dynamic.itb
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/reglinux/boot/uboot-bananapi-f3/u-boot.bin $(BINARIES_DIR)/uboot-bananapi-f3/u-boot.bin
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/reglinux/boot/uboot-bananapi-f3/u-boot.itb $(BINARIES_DIR)/uboot-bananapi-f3/u-boot.itb
endef

$(eval $(generic-package))
