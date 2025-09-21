################################################################################
#
# retroarch-assets
#
################################################################################

RETROARCH_ASSETS_VERSION = v1.20.0
RETROARCH_ASSETS_SITE = $(call github,libretro,retroarch-assets,$(RETROARCH_ASSETS_VERSION))
RETROARCH_ASSETS_LICENSE = GPL

define RETROARCH_ASSETS_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/usr/share/libretro/assets/xmb
	cp -r $(@D)/rgui $(TARGET_DIR)/usr/share/libretro/assets
	cp -r $(@D)/glui $(TARGET_DIR)/usr/share/libretro/assets
	cp -r $(@D)/xmb/monochrome $(TARGET_DIR)/usr/share/libretro/assets/xmb
endef

define RETROARCH_ASSETS_INSTALL_OZONE_ASSETS
	cp -r $(@D)/ozone $(TARGET_DIR)/usr/share/libretro/assets
endef

# Ozone is only compiled and used on GLES 3.0 devices
ifeq ($(BR2_PACKAGE_HAS_GLES3),y)
RETROARCH_ASSETS_POST_INSTALL_TARGET_HOOKS += RETROARCH_ASSETS_INSTALL_OZONE_ASSETS
endif

$(eval $(generic-package))
