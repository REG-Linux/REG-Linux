################################################################################
#
# retroarch-joypad-autoconfig
#
################################################################################

RETROARCH_JOYPAD_AUTOCONFIG_VERSION = v1.22.0
RETROARCH_JOYPAD_AUTOCONFIG_SITE = $(call github,libretro,retroarch-joypad-autoconfig,$(RETROARCH_JOYPAD_AUTOCONFIG_VERSION))
RETROARCH_JOYPAD_AUTOCONFIG_LICENSE = MIT
RETROARCH_JOYPAD_AUTOCONFIG_LICENSE_FILES = LICENSE

# Installation directory for autoconfig profiles
RETROARCH_JOYPAD_AUTOCONFIG_INSTALL_DIR = $(TARGET_DIR)/usr/share/reglinux/datainit/system/configs/retroarch/autoconfig

# Install stock libretro autoconfig profiles for all input drivers
# REG-Linux uses SDL2 as the default joypad driver
define RETROARCH_JOYPAD_AUTOCONFIG_INSTALL_TARGET_CMDS
	# Create autoconfig directory structure
	$(INSTALL) -d $(RETROARCH_JOYPAD_AUTOCONFIG_INSTALL_DIR)

	# Install official libretro profiles for each input driver
	# SDL2 is the primary driver for REG-Linux
	$(INSTALL) -d $(RETROARCH_JOYPAD_AUTOCONFIG_INSTALL_DIR)/hid
	cp -r $(@D)/hid/* $(RETROARCH_JOYPAD_AUTOCONFIG_INSTALL_DIR)/hid/

	$(INSTALL) -d $(RETROARCH_JOYPAD_AUTOCONFIG_INSTALL_DIR)/linuxraw
	cp -r $(@D)/linuxraw/* $(RETROARCH_JOYPAD_AUTOCONFIG_INSTALL_DIR)/linuxraw/

	$(INSTALL) -d $(RETROARCH_JOYPAD_AUTOCONFIG_INSTALL_DIR)/sdl2
	cp -r $(@D)/sdl2/* $(RETROARCH_JOYPAD_AUTOCONFIG_INSTALL_DIR)/sdl2/

	$(INSTALL) -d $(RETROARCH_JOYPAD_AUTOCONFIG_INSTALL_DIR)/udev
	cp -r $(@D)/udev/* $(RETROARCH_JOYPAD_AUTOCONFIG_INSTALL_DIR)/udev/

	$(INSTALL) -d $(RETROARCH_JOYPAD_AUTOCONFIG_INSTALL_DIR)/x
	cp -r $(@D)/x/* $(RETROARCH_JOYPAD_AUTOCONFIG_INSTALL_DIR)/x/

	$(INSTALL) -d $(RETROARCH_JOYPAD_AUTOCONFIG_INSTALL_DIR)/xinput
	cp -r $(@D)/xinput/* $(RETROARCH_JOYPAD_AUTOCONFIG_INSTALL_DIR)/xinput/
endef

$(eval $(generic-package))
