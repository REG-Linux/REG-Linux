################################################################################
#
# SDLPoP
#
################################################################################
# Version.: Commits on Apr 20, 2025
SDLPOP_VERSION = v1.24-RC
SDLPOP_SITE = $(call github,NagyD,SDLPoP,$(SDLPOP_VERSION))
SDLPOP_SUBDIR = src
SDLPOP_LICENSE = GPLv3
SDLPOP_DEPENDENCIES = sdl2 sdl2_image

define SDLPOP_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/usr/share/reglinux/datainit/roms/
	cp -pr $(SDLPOP_PKGDIR)/sdlpop $(TARGET_DIR)/usr/share/reglinux/datainit/roms/
	cp -pr $(@D)/data $(TARGET_DIR)/usr/share/reglinux/datainit/roms/sdlpop/
	$(INSTALL) -D -m 0755 $(@D)/prince $(TARGET_DIR)/usr/bin/SDLPoP
	$(INSTALL) -m 0644 $(@D)/SDLPoP.ini $(TARGET_DIR)/usr/share/reglinux/datainit/roms/sdlpop/SDLPoP.ini
endef

$(eval $(cmake-package))
