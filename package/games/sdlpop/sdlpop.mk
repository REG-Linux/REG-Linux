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
	mkdir -p $(TARGET_DIR)/usr/share/SDLPoP
	mkdir -p $(TARGET_DIR)/usr/share/evmapy
	mkdir -p $(TARGET_DIR)/usr/share/SDLPoP/cfg
	$(INSTALL) -m 0755 $(@D)/prince -D $(TARGET_DIR)/usr/bin/SDLPoP
	cp $(@D)/SDLPoP.ini $(TARGET_DIR)/usr/share/SDLPoP/cfg/SDLPoP.ini
	echo "# Blank cfg file for advanced configuration" > \
	    $(TARGET_DIR)/usr/share/SDLPoP/cfg/SDLPoP.cfg
	cp -pr $(@D)/data $(TARGET_DIR)/usr/share/SDLPoP/
	cp $(BR2_EXTERNAL_REGLINUX_PATH)/package/games/sdlpop/sdlpop.keys $(TARGET_DIR)/usr/share/evmapy
endef

$(eval $(cmake-package))
