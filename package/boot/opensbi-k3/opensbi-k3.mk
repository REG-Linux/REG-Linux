################################################################################
#
# opensbi-k3 - Wrap mainline OpenSBI fw_dynamic.bin into FIT image for K3 SPL
#
# The .its uses load/entry = <0 0> (fw_dynamic is relocatable); the actual
# load address is set by U-Boot SPL (CONFIG_SPL_OPENSBI_LOAD_ADDR=0x100000000
# on K3), so the descriptor is shared verbatim with opensbi-k1.
#
################################################################################

OPENSBI_K3_VERSION = 1.0
OPENSBI_K3_SOURCE =
OPENSBI_K3_INSTALL_TARGET = NO
OPENSBI_K3_INSTALL_STAGING = NO
OPENSBI_K3_INSTALL_IMAGES = YES
OPENSBI_K3_DEPENDENCIES = opensbi host-dtc host-uboot-tools

define OPENSBI_K3_INSTALL_IMAGES_CMDS
	mkdir -p $(BINARIES_DIR)/uboot-k3
	cp $(OPENSBI_K3_PKGDIR)/fw_dynamic.its $(BINARIES_DIR)/fw_dynamic.its
	PATH="$(HOST_DIR)/bin:$(PATH)" \
		$(HOST_DIR)/bin/mkimage -f $(BINARIES_DIR)/fw_dynamic.its \
		-r $(BINARIES_DIR)/uboot-k3/fw_dynamic.itb
endef

$(eval $(generic-package))
