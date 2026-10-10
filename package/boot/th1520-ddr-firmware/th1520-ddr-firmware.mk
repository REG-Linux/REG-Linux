################################################################################
#
# TH1520 DDR firmware
#
################################################################################

TH1520_DDR_FIRMWARE_VERSION = db8df6cab3ff2a935eced5327b49a7465ec135d8
TH1520_DDR_FIRMWARE_SITE = https://github.com/ziyao233/th1520-firmware.git
TH1520_DDR_FIRMWARE_SITE_METHOD = git
TH1520_DDR_FIRMWARE_INSTALL_TARGET = NO
TH1520_DDR_FIRMWARE_INSTALL_STAGING = NO
TH1520_DDR_FIRMWARE_INSTALL_IMAGES = YES
TH1520_DDR_FIRMWARE_DEPENDENCIES = host-lua

define TH1520_DDR_FIRMWARE_BUILD_CMDS
	cd $(@D) && $(HOST_DIR)/bin/lua ddr-generate.lua src/lpddr4x-3733-dualrank.lua th1520-ddr-firmware.bin
endef

define TH1520_DDR_FIRMWARE_INSTALL_IMAGES_CMDS
	cp $(@D)/th1520-ddr-firmware.bin $(BINARIES_DIR)/th1520-ddr-firmware.bin
endef

$(eval $(generic-package))
