################################################################################
#
# opensbi-k1 - Wrap mainline OpenSBI fw_dynamic.bin into FIT image for K1 SPL
#
################################################################################

OPENSBI_K1_VERSION = 1.0
OPENSBI_K1_SOURCE =
OPENSBI_K1_INSTALL_TARGET = NO
OPENSBI_K1_INSTALL_STAGING = NO
OPENSBI_K1_INSTALL_IMAGES = YES
OPENSBI_K1_DEPENDENCIES = opensbi host-dtc host-uboot-tools

define OPENSBI_K1_INSTALL_IMAGES_CMDS
	mkdir -p $(BINARIES_DIR)/uboot-bananapi-f3
	mkdir -p $(BINARIES_DIR)/uboot-orangepi-rv2
	cp $(OPENSBI_K1_PKGDIR)/fw_dynamic.its $(BINARIES_DIR)/fw_dynamic.its
	PATH="$(HOST_DIR)/bin:$(PATH)" \
		$(HOST_DIR)/bin/mkimage -f $(BINARIES_DIR)/fw_dynamic.its \
		-r $(BINARIES_DIR)/uboot-bananapi-f3/fw_dynamic.itb
	cp $(BINARIES_DIR)/uboot-bananapi-f3/fw_dynamic.itb \
		$(BINARIES_DIR)/uboot-orangepi-rv2/fw_dynamic.itb
endef

$(eval $(generic-package))
