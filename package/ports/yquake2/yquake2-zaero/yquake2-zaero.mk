################################################################################
#
# Yamagi Quake 2 (Zaero)
#
################################################################################
# Version: Commits on Dec 29, 2025
YQUAKE2_ZAERO_VERSION = 16d74a82ddbe0e881425268ea73ec2b4947c7e9e
YQUAKE2_ZAERO_SITE = https://github.com/yquake2/zaero.git
YQUAKE2_ZAERO_SITE_METHOD = git
YQUAKE2_ZAERO_DEPENDENCIES = sdl2

YQUAKE2_ZAERO_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release

# Installed under datainit alongside yquake2-client so first-boot populate
# lands game.so in /userdata/roms/quake2/zaero next to the user's own .pak
# files (see package/ports/yquake2/yquake2-client/yquake2-client.mk).
define YQUAKE2_ZAERO_INSTALL_TARGET_CMDS
        mkdir -p $(TARGET_DIR)/usr/share/reglinux/datainit/roms/quake2/zaero/
        $(INSTALL) -D -m 0755 $(@D)/Release/game.so $(TARGET_DIR)/usr/share/reglinux/datainit/roms/quake2/zaero/game.so
endef

$(eval $(cmake-package))
