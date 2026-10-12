################################################################################
#
# mkxp-z — RPG Maker XP/VX/VX Ace player ("RGSS on steroids")
#
################################################################################

MKXP_Z_VERSION = 01efd999573ad416a01393d8ce62b78f06976e2c
MKXP_Z_SITE = https://github.com/mkxp-z/mkxp-z
MKXP_Z_SITE_METHOD = git
MKXP_Z_GIT_LFS = NO

MKXP_Z_LICENSE = GPL-2.0+
MKXP_Z_LICENSE_FILES = COPYING

MKXP_Z_DEPENDENCIES = sdl2 sdl2_image sdl2_ttf sdl_sound \
	openal physfs pixman libvorbis libogg libtheora \
	freetype libpng zlib ruby libiconv dbus uchardet

# mkxp-z uses meson, link against system shared libs
MKXP_Z_CONF_OPTS = \
	-Dmri_version=3.4 \
	-Dstatic_executable=false \
	-Dshared_fluid=true \
	-Denable-https=false \
	-Duse_miniffi=true \
	-Dcjk_fallback_font=false \
	-Dworkdir_current=false

ifeq ($(BR2_PACKAGE_HAS_LIBGLES),y)
MKXP_Z_CONF_OPTS += -Dgfx_backend=gles
MKXP_Z_DEPENDENCIES += libgles
else
MKXP_Z_CONF_OPTS += -Dgfx_backend=gl
MKXP_Z_DEPENDENCIES += libgl
endif

ifeq ($(BR2_PACKAGE_FLUIDSYNTH),y)
MKXP_Z_DEPENDENCIES += fluidsynth
endif

ifeq ($(BR2_PACKAGE_OPENSSL),y)
MKXP_Z_DEPENDENCIES += openssl
MKXP_Z_CONF_OPTS += -Denable-https=true
endif

define MKXP_Z_INSTALL_TARGET_CMDS
	$(INSTALL) -D -m 0755 $(@D)/build/mkxp-z $(TARGET_DIR)/usr/bin/mkxp-z
endef

$(eval $(meson-package))
