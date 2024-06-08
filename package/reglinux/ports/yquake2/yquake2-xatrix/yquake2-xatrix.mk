################################################################################
#
# Yamagi Quake 2 (Xatrix)
#
################################################################################

YQUAKE2_XATRIX_VERSION = XATRIX_2_12
YQUAKE2_XATRIX_SITE = $(call github,yquake2,xatrix,$(YQUAKE2_XATRIX_VERSION))
YQUAKE2_XATRIX_DEPENDENCIES = sdl2

YQUAKE2_XATRIX_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release

# Install game library
define YQUAKE2_XATRIX_INSTALL_TARGET_CMDS
        mkdir -p $(TARGET_DIR)/usr/yquake2/xatrix/
        $(INSTALL) -D -m 0755 $(@D)/Release/game.so $(TARGET_DIR)/usr/yquake2/xatrix/game.so
endef

$(eval $(cmake-package))
