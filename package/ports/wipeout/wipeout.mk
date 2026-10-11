################################################################################
#
# wipeout — Wipeout (PSX) engine reimplementation
#
################################################################################

WIPEOUT_VERSION = 55fd79749ea69d8dce99326830cb0c5097994bca
WIPEOUT_SITE = https://github.com/phoboslab/wipeout-rewrite.git
WIPEOUT_SITE_METHOD = git
WIPEOUT_SUPPORTS_IN_SOURCE_BUILD = NO

WIPEOUT_LICENSE = Custom (phoboslab)

WIPEOUT_DEPENDENCIES = sdl2

WIPEOUT_CONF_OPTS = \
	-DCMAKE_BUILD_TYPE=Release \
	-DPLATFORM=SDL2

ifeq ($(BR2_PACKAGE_HAS_LIBGL),y)
WIPEOUT_DEPENDENCIES += libgl libglew
WIPEOUT_CONF_OPTS += -DRENDERER=GL
else ifeq ($(BR2_PACKAGE_HAS_LIBGLES),y)
WIPEOUT_DEPENDENCIES += libgles
WIPEOUT_CONF_OPTS += -DRENDERER=GLES2
else
WIPEOUT_CONF_OPTS += -DRENDERER=SOFTWARE
endif

define WIPEOUT_INSTALL_TARGET_CMDS
	$(INSTALL) -D -m 0755 $(@D)/wipeout $(TARGET_DIR)/usr/bin/wipeout
endef

$(eval $(cmake-package))
