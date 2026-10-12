################################################################################
#
# retroachievements-sounds
#
################################################################################

define RETROACHIEVEMENTS_SOUNDS_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/usr/share/libretro/assets/sounds/
	cp -r $(RETROACHIEVEMENTS_SOUNDS_PKGDIR)/sounds/*.ogg $(TARGET_DIR)/usr/share/libretro/assets/sounds/
endef

$(eval $(generic-package))
