################################################################################
#
# uboot for BeagleV Ahead - vendor pre-built from RevyOS
#
################################################################################

UBOOT_BEAGLEV_AHEAD_VERSION = 20260504
UBOOT_BEAGLEV_AHEAD_SOURCE = u-boot-with-spl-beagle.bin
UBOOT_BEAGLEV_AHEAD_SITE = https://github.com/revyos/thead-u-boot/releases/download/$(UBOOT_BEAGLEV_AHEAD_VERSION)
UBOOT_BEAGLEV_AHEAD_INSTALL_TARGET = NO
UBOOT_BEAGLEV_AHEAD_INSTALL_STAGING = NO
UBOOT_BEAGLEV_AHEAD_INSTALL_IMAGES = YES

define UBOOT_BEAGLEV_AHEAD_EXTRACT_CMDS
	cp $(UBOOT_BEAGLEV_AHEAD_DL_DIR)/$(UBOOT_BEAGLEV_AHEAD_SOURCE) $(@D)/u-boot-with-spl-beagle.bin
endef

define UBOOT_BEAGLEV_AHEAD_INSTALL_IMAGES_CMDS
	mkdir -p $(BINARIES_DIR)/uboot-beaglev-ahead
	cp $(@D)/u-boot-with-spl-beagle.bin $(BINARIES_DIR)/uboot-beaglev-ahead/u-boot-with-spl-beagle.bin
	# Patch vendor U-Boot default env: boot from partition 1 (REG-Linux layout)
	sed -i 's/mmcbootpart=2/mmcbootpart=1/' $(BINARIES_DIR)/uboot-beaglev-ahead/u-boot-with-spl-beagle.bin
endef

$(eval $(generic-package))
