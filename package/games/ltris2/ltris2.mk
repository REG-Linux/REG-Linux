################################################################################
#
# ltris2
#
################################################################################

LTRIS2_VERSION = 2.0.4
LTRIS2_SITE = http://downloads.sourceforge.net/lgames/ltris
LTRIS2_LICENSE = GPL-2.0+
LTRIS2_LICENSE_FILES = COPYING

LTRIS2_DEPENDENCIES = sdl2 sdl2_image sdl2_mixer sdl2_ttf host-pkgconf $(TARGET_NLS_DEPENDENCIES)
LTRIS2_LIBS = $(TARGET_NLS_LIBS)

LTRIS2_CONF_ENV = \
	SDL2_CONFIG="$(STAGING_DIR)/usr/bin/sdl2-config" \
	LIBS="$(LTRIS2_LIBS)"

$(eval $(autotools-package))
