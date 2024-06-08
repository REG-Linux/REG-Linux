################################################################################
#
# Yamagi Quake 2 (Capture The Flag)
#
################################################################################

YQUAKE2_CTF_VERSION = CTF_1_10
YQUAKE2_CTF_SITE = $(call github,yquake2,ctf,$(YQUAKE2_CTF_VERSION))
YQUAKE2_CTF_DEPENDENCIES = sdl2

YQUAKE2_CTF_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release

# Install game library
define YQUAKE2_CTF_INSTALL_TARGET_CMDS
        mkdir -p $(TARGET_DIR)/usr/yquake2/ctf/
        $(INSTALL) -D -m 0755 $(@D)/Release/game.so $(TARGET_DIR)/usr/yquake2/ctf/game.so
endef

$(eval $(cmake-package))
