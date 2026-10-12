################################################################################
#
# Yamagi Quake 2 (Capture The Flag)
#
################################################################################

YQUAKE2_CTF_VERSION = CTF_1_13
YQUAKE2_CTF_SITE = $(call github,yquake2,ctf,$(YQUAKE2_CTF_VERSION))
YQUAKE2_CTF_DEPENDENCIES = sdl2

YQUAKE2_CTF_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release

# Installed under datainit alongside yquake2-client so first-boot populate
# lands game.so in /userdata/roms/quake2/ctf next to the user's own .pak
# files (see package/ports/yquake2/yquake2-client/yquake2-client.mk).
define YQUAKE2_CTF_INSTALL_TARGET_CMDS
        mkdir -p $(TARGET_DIR)/usr/share/reglinux/datainit/roms/quake2/ctf/
        $(INSTALL) -D -m 0755 $(@D)/Release/game.so $(TARGET_DIR)/usr/share/reglinux/datainit/roms/quake2/ctf/game.so
endef

$(eval $(cmake-package))
