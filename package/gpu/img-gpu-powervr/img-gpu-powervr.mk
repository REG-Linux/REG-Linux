################################################################################
#
# img-gpu-powervr binary package
#
################################################################################

ifeq ($(BR2_PACKAGE_SYSTEM_TARGET_K1),y)
IMG_GPU_POWERVR_VERSION = k1-bl-v2.2-release
IMG_GPU_POWERVR_SITE = https://gitee.com/bianbu-linux/img-gpu-powervr.git
IMG_GPU_POWERVR_SITE_METHOD = git
else
IMG_GPU_POWERVR_VERSION = 1.19
IMG_GPU_POWERVR_SOURCE = img-gpu-powervr-bin-1.19.6345021.tar.gz
IMG_GPU_POWERVR_SITE = https://github.com/starfive-tech/soft_3rdpart/raw/JH7110_VisionFive2_devel/IMG_GPU/out
endif
IMG_GPU_POWERVR_INSTALL_STAGING = YES

IMG_GPU_POWERVR_LICENSE = Strictly Confidential
IMG_GPU_POWERVR_REDISTRIBUTE = NO

IMG_GPU_POWERVR_PROVIDES = libgles libopencl

IMG_GPU_POWERVR_DEPENDENCIES += libdrm img-mesa3d

ifeq ($(BR2_PACKAGE_WAYLAND),y)
IMG_GPU_POWERVR_DEPENDENCIES += wayland
endif

define IMG_GPU_POWERVR_INSTALL_STAGING_CMDS
	cp -rdpf $(@D)/staging/* $(STAGING_DIR)/
	mkdir -p $(STAGING_DIR)/usr/lib/pkgconfig
	cp $(@D)/staging/usr/lib/glesv2.pc $(STAGING_DIR)/usr/lib/pkgconfig/
	mkdir -p $(STAGING_DIR)/usr/include
	cp -rdpf $(@D)/staging/include/* $(STAGING_DIR)/usr/include/
endef

define IMG_GPU_POWERVR_INSTALL_TARGET_CMDS
	cp -rdpf $(@D)/target/* $(TARGET_DIR)/
endef

$(eval $(generic-package))
