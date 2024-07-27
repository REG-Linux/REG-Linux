################################################################################
#
# Yamagi Quake 2 (Rogue)
#
################################################################################

YQUAKE2_ROGUE_VERSION = ROGUE_2_12
YQUAKE2_ROGUE_SITE = $(call github,yquake2,rogue,$(YQUAKE2_ROGUE_VERSION))
YQUAKE2_ROGUE_DEPENDENCIES = sdl2

YQUAKE2_ROGUE_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release

# Install game library
define YQUAKE2_ROGUE_INSTALL_TARGET_CMDS
        mkdir -p $(TARGET_DIR)/usr/yquake2/rogue/
        $(INSTALL) -D -m 0755 $(@D)/Release/game.so $(TARGET_DIR)/usr/yquake2/rogue/game.so
endef

$(eval $(cmake-package))
