################################################################################
#
# Yamagi Quake 2
#
################################################################################

YQUAKE2_CLIENT_VERSION = QUAKE2_8_40
YQUAKE2_CLIENT_SITE = $(call github,yquake2,yquake2,$(YQUAKE2_CLIENT_VERSION))
YQUAKE2_CLIENT_DEPENDENCIES = sdl2

YQUAKE2_CLIENT_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release

# Install binaries, renderers and base game library
define YQUAKE2_CLIENT_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/usr/yquake2/baseq2/
	$(INSTALL) -D -m 0755 $(@D)/release/quake2         $(TARGET_DIR)/usr/yquake2/quake2
	$(INSTALL) -D -m 0755 $(@D)/release/q2ded          $(TARGET_DIR)/usr/yquake2/q2ded
	$(INSTALL) -D -m 0755 $(@D)/release/ref_gl1.so     $(TARGET_DIR)/usr/yquake2/ref_gl1.so
	$(INSTALL) -D -m 0755 $(@D)/release/ref_gl3.so     $(TARGET_DIR)/usr/yquake2/ref_gl3.so
	$(INSTALL) -D -m 0755 $(@D)/release/ref_gles3.so   $(TARGET_DIR)/usr/yquake2/ref_gles3.so
	$(INSTALL) -D -m 0755 $(@D)/release/ref_soft.so    $(TARGET_DIR)/usr/yquake2/ref_soft.so
	$(INSTALL) -D -m 0755 $(@D)/release/baseq2/game.so $(TARGET_DIR)/usr/yquake2/baseq2/game.so
endef

$(eval $(cmake-package))
