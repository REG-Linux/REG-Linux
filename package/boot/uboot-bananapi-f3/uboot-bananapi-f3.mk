################################################################################
#
# uboot for BananaPi F3 / SpaceMiT K1 - built from source
#
################################################################################

UBOOT_BANANAPI_F3_VERSION = k1-bl-v2.2.9-release
UBOOT_BANANAPI_F3_SITE = https://github.com/spacemit-com/uboot-2022.10.git
UBOOT_BANANAPI_F3_SITE_METHOD = git
UBOOT_BANANAPI_F3_INSTALL_TARGET = NO
UBOOT_BANANAPI_F3_INSTALL_STAGING = NO
UBOOT_BANANAPI_F3_INSTALL_IMAGES = YES
UBOOT_BANANAPI_F3_DEPENDENCIES = opensbi host-flex host-uboot-tools

UBOOT_BANANAPI_F3_MAKE_OPTS = \
	CROSS_COMPILE=$(TARGET_CROSS)

define UBOOT_BANANAPI_F3_BUILD_CMDS
	$(TARGET_MAKE_ENV) $(MAKE) -C $(@D) $(UBOOT_BANANAPI_F3_MAKE_OPTS) k1_defconfig
	$(TARGET_MAKE_ENV) $(MAKE) -C $(@D) $(UBOOT_BANANAPI_F3_MAKE_OPTS)
endef

define UBOOT_BANANAPI_F3_INSTALL_IMAGES_CMDS
	mkdir -p $(BINARIES_DIR)/uboot-bananapi-f3
	cp $(@D)/FSBL.bin               $(BINARIES_DIR)/uboot-bananapi-f3/FSBL.bin
	cp $(@D)/u-boot.itb             $(BINARIES_DIR)/uboot-bananapi-f3/u-boot.itb
	cp $(@D)/bootinfo_sd.bin        $(BINARIES_DIR)/uboot-bananapi-f3/bootinfo_sd.bin
	cp $(@D)/bootinfo_emmc.bin      $(BINARIES_DIR)/uboot-bananapi-f3/bootinfo_emmc.bin
	cp $(@D)/u-boot-env-default.bin $(BINARIES_DIR)/uboot-bananapi-f3/env.bin
endef

$(eval $(generic-package))
