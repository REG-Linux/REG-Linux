################################################################################
#
# NakedAVP — Aliens versus Predator (1999) source port
#
################################################################################

NAKEDAVP_VERSION = 1.3.0
NAKEDAVP_SITE = https://github.com/atsb/NakedAVP
NAKEDAVP_SITE_METHOD = git
NAKEDAVP_LICENSE = Custom

NAKEDAVP_DEPENDENCIES = sdl3 openal ffmpeg

NAKEDAVP_SUPPORTS_IN_SOURCE_BUILD = NO

NAKEDAVP_CONF_OPTS = \
	-DCMAKE_BUILD_TYPE=Release \
	-DCMAKE_C_FLAGS="-std=gnu17"

ifeq ($(BR2_PACKAGE_HAS_LIBGL),y)
NAKEDAVP_DEPENDENCIES += libgl
NAKEDAVP_CONF_OPTS += -DOPENGL_TYPE=OPENGL
else ifeq ($(BR2_PACKAGE_HAS_LIBGLES),y)
NAKEDAVP_DEPENDENCIES += libgles libegl
NAKEDAVP_CONF_OPTS += -DOPENGL_TYPE=OPENGLES2
endif

define NAKEDAVP_INSTALL_TARGET_CMDS
	$(INSTALL) -D -m 0755 $(@D)/buildroot-build/avp $(TARGET_DIR)/usr/bin/avp
endef

$(eval $(cmake-package))
