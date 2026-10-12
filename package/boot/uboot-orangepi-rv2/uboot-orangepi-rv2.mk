################################################################################
#
# uboot for OrangePi RV2 / SpaceMiT K1 - built from source
#
################################################################################

UBOOT_ORANGEPI_RV2_VERSION = k1-bl-v2.2.9-release
UBOOT_ORANGEPI_RV2_SITE = https://github.com/spacemit-com/uboot-2022.10.git
UBOOT_ORANGEPI_RV2_SITE_METHOD = git
UBOOT_ORANGEPI_RV2_INSTALL_TARGET = NO
UBOOT_ORANGEPI_RV2_INSTALL_STAGING = NO
UBOOT_ORANGEPI_RV2_INSTALL_IMAGES = YES
UBOOT_ORANGEPI_RV2_DEPENDENCIES = opensbi host-flex host-uboot-tools

UBOOT_ORANGEPI_RV2_MAKE_OPTS = \
	CROSS_COMPILE=$(TARGET_CROSS)

define UBOOT_ORANGEPI_RV2_BUILD_CMDS
	$(TARGET_MAKE_ENV) $(MAKE) -C $(@D) $(UBOOT_ORANGEPI_RV2_MAKE_OPTS) k1_defconfig
	$(@D)/scripts/config --file $(@D)/.config --disable CONFIG_MMC_UHS_SUPPORT
	$(TARGET_MAKE_ENV) $(MAKE) -C $(@D) $(UBOOT_ORANGEPI_RV2_MAKE_OPTS)
endef

define UBOOT_ORANGEPI_RV2_INSTALL_IMAGES_CMDS
	mkdir -p $(BINARIES_DIR)/uboot-orangepi-rv2
	cp $(@D)/FSBL.bin               $(BINARIES_DIR)/uboot-orangepi-rv2/FSBL.bin
	cp $(@D)/u-boot.itb             $(BINARIES_DIR)/uboot-orangepi-rv2/u-boot.itb
	cp $(@D)/bootinfo_sd.bin        $(BINARIES_DIR)/uboot-orangepi-rv2/bootinfo_sd.bin
	cp $(@D)/bootinfo_emmc.bin      $(BINARIES_DIR)/uboot-orangepi-rv2/bootinfo_emmc.bin
	cp $(@D)/u-boot-env-default.bin $(BINARIES_DIR)/uboot-orangepi-rv2/env.bin
endef

$(eval $(generic-package))
