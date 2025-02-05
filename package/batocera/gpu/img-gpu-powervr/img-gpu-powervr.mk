################################################################################
#
# img-gpu-powervr binary package
#
################################################################################

#ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_JH7110),y)
#IMG_GPU_POWERVR_VERSION = 1.19
#IMG_GPU_POWERVR_SOURCE=img-gpu-powervr-bin-1.19.6345021.tar.gz
#IMG_GPU_POWERVR_SITE = https://github.com/starfive-tech/soft_3rdpart/raw/JH7110_VisionFive2_devel/IMG_GPU/out
#else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_K1),y)
IMG_GPU_POWERVR_VERSION = bl-v2.0.y
IMG_GPU_POWERVR_SITE = https://gitee.com/bianbu-linux/img-gpu-powervr.git
IMG_GPU_POWERVR_SITE_METHOD = git
#endif

IMG_GPU_POWERVR_INSTALL_STAGING = YES

IMG_GPU_POWERVR_LICENSE = Strictly Confidential
IMG_GPU_POWERVR_REDISTRIBUTE = NO

IMG_GPU_POWERVR_DEPENDENCIES += libdrm img-mesa3d

# Hack because blob overwrite vulkan-headers
#IMG_GPU_POWERVR_DEPENDENCIES += vulkan-headers

ifeq ($(BR2_PACKAGE_WAYLAND),y)
IMG_GPU_POWERVR_DEPENDENCIES += wayland
endif

define IMG_GPU_POWERVR_INSTALL_STAGING_CMDS
	cp -rdpf $(@D)/staging/include/* $(STAGING_DIR)/usr/include/
	cp -rdpf $(@D)/staging/usr/lib/* $(STAGING_DIR)/usr/lib/
	# Fix
	mv $(STAGING_DIR)/usr/lib/glesv2.pc $(STAGING_DIR)/usr/lib/pkgconfig/glesv2.pc
endef

define IMG_GPU_POWERVR_INSTALL_TARGET_CMDS
	cp -rdpf $(@D)/target/* $(TARGET_DIR)/
endef

$(eval $(generic-package))
