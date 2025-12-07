################################################################################
#
# uboot files for Khadas Edge 2
#
################################################################################

UBOOT_KHADAS_EDGE_2_VERSION = armbian-legacy-2025.08
UBOOT_KHADAS_EDGE_2_SOURCE =

define UBOOT_KHADAS_EDGE_2_BUILD_CMDS
endef

define UBOOT_KHADAS_EDGE_2_INSTALL_TARGET_CMDS
	mkdir -p $(BINARIES_DIR)/uboot-khadas-edge-2
	cp $(BR2_EXTERNAL_REGLINUX_PATH)/package/boot/uboot-khadas-edge-2/idbloader.img $(BINARIES_DIR)/uboot-khadas-edge-2/idbloader.img
	cp $(BR2_EXTERNAL_REGLINUX_PATH)/package/boot/uboot-khadas-edge-2/u-boot.itb $(BINARIES_DIR)/uboot-khadas-edge-2/u-boot.itb
endef

$(eval $(generic-package))
