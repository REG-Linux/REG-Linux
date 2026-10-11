################################################################################
#
# Yamagi Quake 2 (Xatrix)
#
################################################################################

YQUAKE2_XATRIX_VERSION = XATRIX_2_17
YQUAKE2_XATRIX_SITE = $(call github,yquake2,xatrix,$(YQUAKE2_XATRIX_VERSION))
YQUAKE2_XATRIX_DEPENDENCIES = sdl2

YQUAKE2_XATRIX_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release

# Installed under datainit alongside yquake2-client so first-boot populate
# lands game.so in /userdata/roms/quake2/xatrix next to the user's own .pak
# files (see package/ports/yquake2/yquake2-client/yquake2-client.mk).
define YQUAKE2_XATRIX_INSTALL_TARGET_CMDS
        mkdir -p $(TARGET_DIR)/usr/share/reglinux/datainit/roms/quake2/xatrix/
        $(INSTALL) -D -m 0755 $(@D)/Release/game.so $(TARGET_DIR)/usr/share/reglinux/datainit/roms/quake2/xatrix/game.so
endef

$(eval $(cmake-package))
