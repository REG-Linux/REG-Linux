################################################################################
#
# uboot for SpacemiT K3 - built from source
#
# A single k3_defconfig (CONFIG_TARGET_SPACEMIT_K3) serves every K3 board; the
# board variant is selected at runtime via the kernel DTB (extlinux FDT line),
# so one generic package covers all K3 boards (CoM260, Pico-ITX, ...).
#
################################################################################

UBOOT_K3_VERSION = k3-br-v1.0.y
UBOOT_K3_SITE = https://github.com/spacemit-com/uboot-2022.10.git
UBOOT_K3_SITE_METHOD = git
UBOOT_K3_INSTALL_TARGET = NO
UBOOT_K3_INSTALL_STAGING = NO
UBOOT_K3_INSTALL_IMAGES = YES
UBOOT_K3_DEPENDENCIES = opensbi host-flex host-uboot-tools

UBOOT_K3_MAKE_OPTS = \
	CROSS_COMPILE=$(TARGET_CROSS)

define UBOOT_K3_BUILD_CMDS
	$(TARGET_MAKE_ENV) $(MAKE) -C $(@D) $(UBOOT_K3_MAKE_OPTS) k3_defconfig
	$(TARGET_MAKE_ENV) $(MAKE) -C $(@D) $(UBOOT_K3_MAKE_OPTS)
endef

# K3 uboot build outputs (verified against bianbu k3-br-v1.0.y board configs):
# FSBL.bin, u-boot.itb, u-boot-env-default.bin, and a UNIFIED bootinfo_block.bin
# for SD/eMMC/UFS (replaces K1's separate bootinfo_sd.bin + bootinfo_emmc.bin);
# bootinfo_spinor.bin / bootinfo_spinand.bin are the flash-boot variants.
define UBOOT_K3_INSTALL_IMAGES_CMDS
	mkdir -p $(BINARIES_DIR)/uboot-k3
	cp $(@D)/FSBL.bin               $(BINARIES_DIR)/uboot-k3/FSBL.bin
	cp $(@D)/u-boot.itb             $(BINARIES_DIR)/uboot-k3/u-boot.itb
	cp $(@D)/bootinfo_block.bin     $(BINARIES_DIR)/uboot-k3/bootinfo_block.bin
	cp $(@D)/u-boot-env-default.bin $(BINARIES_DIR)/uboot-k3/env.bin
endef

$(eval $(generic-package))
