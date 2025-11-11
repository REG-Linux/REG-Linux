################################################################################
#
# retroarch-joypad-autoconfig
#
################################################################################

RETROARCH_JOYPAD_AUTOCONFIG_VERSION = v1.22.0
RETROARCH_JOYPAD_AUTOCONFIG_SITE = $(call github,libretro,retroarch-joypad-autoconfig,$(RETROARCH_JOYPAD_AUTOCONFIG_VERSION))
RETROARCH_JOYPAD_AUTOCONFIG_LICENSE = MIT

RETROARCH_JOYPAD_AUTOCONFIG_INSTALL_DIR = $(TARGET_DIR)/usr/share/reglinux/datainit/system/configs/retroarch/autoconfig

define RETROARCH_JOYPAD_AUTOCONFIG_INSTALL_TARGET_CMDS
	# Stock config files from libretro
	mkdir -p $(RETROARCH_JOYPAD_AUTOCONFIG_INSTALL_DIR)
	cp -r $(@D)/hid		$(RETROARCH_JOYPAD_AUTOCONFIG_INSTALL_DIR)
	cp -r $(@D)/linuxraw	$(RETROARCH_JOYPAD_AUTOCONFIG_INSTALL_DIR)
	cp -r $(@D)/sdl2	$(RETROARCH_JOYPAD_AUTOCONFIG_INSTALL_DIR)
	cp -r $(@D)/udev	$(RETROARCH_JOYPAD_AUTOCONFIG_INSTALL_DIR)
	cp -r $(@D)/x		$(RETROARCH_JOYPAD_AUTOCONFIG_INSTALL_DIR)
	cp -r $(@D)/xinput	$(RETROARCH_JOYPAD_AUTOCONFIG_INSTALL_DIR)

	# Borrow additional ones from ROCKNIX
	cp -r $(BR2_EXTERNAL_REGLINUX_PATH)/package/retroarch/retroarch-joypad-autoconfig/rocknix/* $(RETROARCH_JOYPAD_AUTOCONFIG_INSTALL_DIR)/udev/
endef

$(eval $(generic-package))
