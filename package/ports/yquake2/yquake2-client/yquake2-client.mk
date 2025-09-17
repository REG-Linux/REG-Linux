################################################################################
#
# Yamagi Quake 2
#
################################################################################

YQUAKE2_CLIENT_VERSION = QUAKE2_8_60
YQUAKE2_CLIENT_SITE = $(call github,yquake2,yquake2,$(YQUAKE2_CLIENT_VERSION))
YQUAKE2_CLIENT_DEPENDENCIES = libcurl

YQUAKE2_CLIENT_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release
YQUAKE2_CLIENT_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release

# Favor SDL3 if available, fallback on SDL2 if not
ifeq ($(BR2_PACKAGE_SDL2),y)
YQUAKE2_CLIENT_DEPENDENCIES += sdl2
endif
ifeq ($(BR2_PACKAGE_SDL3),y)
YQUAKE2_CLIENT_DEPENDENCIES += sdl3
YQUAKE2_CLIENT_CONF_OPTS += -DSDL3_SUPPORT=ON
endif

# OpenGL 1.x and 3.x renderers
define YQUAKE2_CLIENT_INSTALL_GL_RENDERERS
	$(INSTALL) -D -m 0755 $(@D)/release/ref_gl1.so     $(TARGET_DIR)/usr/yquake2/ref_gl1.so
	$(INSTALL) -D -m 0755 $(@D)/release/ref_gl3.so     $(TARGET_DIR)/usr/yquake2/ref_gl3.so
endef
ifeq ($(BR2_PACKAGE_HAS_LIBGL),y)
YQUAKE2_CLIENT_CONF_OPTS += -DGL1_RENDERER=ON
YQUAKE2_CLIENT_CONF_OPTS += -DGL3_RENDERER=ON
YQUAKE2_CLIENT_POST_INSTALL_TARGET_HOOKS += YQUAKE2_CLIENT_INSTALL_GL_RENDERERS
else
YQUAKE2_CLIENT_CONF_OPTS += -DGL1_RENDERER=OFF
YQUAKE2_CLIENT_CONF_OPTS += -DGL3_RENDERER=OFF
endif

# OpenGL ES 3.0 renderer
define YQUAKE2_CLIENT_INSTALL_GLES_RENDERER
	$(INSTALL) -D -m 0755 $(@D)/release/ref_gles3.so   $(TARGET_DIR)/usr/yquake2/ref_gles3.so
endef
ifeq ($(BR2_PACKAGE_HAS_GLES3),y)
YQUAKE2_CLIENT_CONF_OPTS += -DGLES3_RENDERER=ON
YQUAKE2_CLIENT_POST_INSTALL_TARGET_HOOKS += YQUAKE2_CLIENT_INSTALL_GLES_RENDERER
else
YQUAKE2_CLIENT_CONF_OPTS += -DGLES3_RENDERER=OFF
endif

# TODO Vulkan renderer (separate package)

# Install binaries, renderers and base game library
define YQUAKE2_CLIENT_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/usr/yquake2/baseq2/
	$(INSTALL) -D -m 0755 $(@D)/release/quake2         $(TARGET_DIR)/usr/yquake2/quake2
	$(INSTALL) -D -m 0755 $(@D)/release/q2ded          $(TARGET_DIR)/usr/yquake2/q2ded
	$(INSTALL) -D -m 0755 $(@D)/release/ref_soft.so    $(TARGET_DIR)/usr/yquake2/ref_soft.so
	$(INSTALL) -D -m 0755 $(@D)/release/baseq2/game.so $(TARGET_DIR)/usr/yquake2/baseq2/game.so
endef

$(eval $(cmake-package))
