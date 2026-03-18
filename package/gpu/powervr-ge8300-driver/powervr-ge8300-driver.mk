################################################################################
#
# PowerVR GE8300 GPU driver for Allwinner A133
#
################################################################################

POWERVR_GE8300_DRIVER_VERSION = main
POWERVR_GE8300_DRIVER_SITE = https://github.com/knulli-cfw/ge8300-drivers.git
POWERVR_GE8300_DRIVER_SITE_METHOD = git

POWERVR_GE8300_DRIVER_LICENSE = Proprietary
POWERVR_GE8300_DRIVER_REDISTRIBUTE = NO

POWERVR_GE8300_DRIVER_INSTALL_STAGING = YES
POWERVR_GE8300_DRIVER_PROVIDES = libegl libgles

define POWERVR_GE8300_DRIVER_INSTALL_STAGING_CMDS
	mkdir -p $(STAGING_DIR)/usr/include
	cp -r $(@D)/3rdparty/include/khronos/* $(STAGING_DIR)/usr/include/
	cp -r $(@D)/fbdev/glibc/lib64/* $(STAGING_DIR)/usr/lib/
endef

define POWERVR_GE8300_DRIVER_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/usr/lib
	mkdir -p $(TARGET_DIR)/usr/bin
	cp -r $(@D)/fbdev/glibc/lib64/* $(TARGET_DIR)/usr/lib/
	cp $(@D)/fbdev/glibc/bin/pvrsrvctl $(TARGET_DIR)/usr/bin/
endef

$(eval $(generic-package))
