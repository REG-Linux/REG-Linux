################################################################################
#
# uboot for Milk-V Meles - vendor pre-built
#
################################################################################

UBOOT_MILKV_MELES_VERSION = 1.0
UBOOT_MILKV_MELES_SOURCE =

define UBOOT_MILKV_MELES_INSTALL_TARGET_CMDS
	mkdir -p $(BINARIES_DIR)/uboot-milkv-meles
	cp $(BR2_EXTERNAL_REGLINUX_PATH)/package/boot/uboot-milkv-meles/u-boot-with-spl-meles-4g.bin  $(BINARIES_DIR)/uboot-milkv-meles/
	cp $(BR2_EXTERNAL_REGLINUX_PATH)/package/boot/uboot-milkv-meles/u-boot-with-spl-meles-8g.bin  $(BINARIES_DIR)/uboot-milkv-meles/
	cp $(BR2_EXTERNAL_REGLINUX_PATH)/package/boot/uboot-milkv-meles/u-boot-with-spl-meles-16g.bin $(BINARIES_DIR)/uboot-milkv-meles/
	# Patch vendor U-Boot default env: boot from partition 1 (REG-Linux layout)
	# instead of partition 2 (vendor layout). No CRC — this is the compiled-in default env.
	sed -i 's/mmcbootpart=2/mmcbootpart=1/' $(BINARIES_DIR)/uboot-milkv-meles/u-boot-with-spl-meles-4g.bin
	sed -i 's/mmcbootpart=2/mmcbootpart=1/' $(BINARIES_DIR)/uboot-milkv-meles/u-boot-with-spl-meles-8g.bin
	sed -i 's/mmcbootpart=2/mmcbootpart=1/' $(BINARIES_DIR)/uboot-milkv-meles/u-boot-with-spl-meles-16g.bin
endef

$(eval $(generic-package))
