################################################################################
#
# rockchip-rkbin
#
################################################################################

# reglinux - bump
ROCKCHIP_RKBIN_VERSION = 7c35e21a8529b3758d1f051d1a5dc62aae934b2b
ROCKCHIP_RKBIN_SITE = https://github.com/rockchip-linux/rkbin.git
ROCKCHIP_RKBIN_SITE_METHOD = git
ROCKCHIP_RKBIN_LICENSE = PROPRIETARY
ROCKCHIP_RKBIN_LICENSE_FILES = LICENSE

ROCKCHIP_RKBIN_INSTALL_IMAGES = YES
ROCKCHIP_RKBIN_INSTALL_TARGET = NO

ROCKCHIP_RKBIN_BL31_FILENAME = $(call qstrip,$(BR2_PACKAGE_ROCKCHIP_RKBIN_BL31_FILENAME))
ROCKCHIP_RKBIN_TPL_FILENAME = $(call qstrip,$(BR2_PACKAGE_ROCKCHIP_RKBIN_TPL_FILENAME))
ROCKCHIP_RKBIN_TEE_FILENAME = $(call qstrip,$(BR2_PACKAGE_ROCKCHIP_RKBIN_TEE_FILENAME))

define ROCKCHIP_RKBIN_INSTALL_IMAGES_CMDS
	$(foreach f, \
		$(ROCKCHIP_RKBIN_BL31_FILENAME) \
		$(ROCKCHIP_RKBIN_TPL_FILENAME) \
		$(ROCKCHIP_RKBIN_TEE_FILENAME) \
		, \
		$(INSTALL) -D -m 0644 -t $(BINARIES_DIR) $(@D)/$(f)
	)
endef

$(eval $(generic-package))
