################################################################################
#
# retroarch-joypad-autoconfig
#
################################################################################

RETROARCH_JOYPAD_AUTOCONFIG_VERSION = v1.20.0
RETROARCH_JOYPAD_AUTOCONFIG_SITE = $(call github,libretro,retroarch-joypad-autoconfig,$(RETROARCH_JOYPAD_AUTOCONFIG_VERSION))
RETROARCH_JOYPAD_AUTOCONFIG_LICENSE = MIT

define RETROARCH_JOYPAD_AUTOCONFIG_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/usr/share/libretro/autoconfig
	cp -r $(@D)/hid $(TARGET_DIR)/usr/share/libretro/autoconfig
	cp -r $(@D)/linuxraw $(TARGET_DIR)/usr/share/libretro/autoconfig
	cp -r $(@D)/sdl2 $(TARGET_DIR)/usr/share/libretro/autoconfig
	cp -r $(@D)/udev $(TARGET_DIR)/usr/share/libretro/autoconfig
endef

$(eval $(generic-package))
