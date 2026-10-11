################################################################################
#
# neverball — Tilt-the-floor ball puzzle game
#
################################################################################

NEVERBALL_VERSION = 58fc1aaab7c0e26e1bdb34c25197329fae5de1a5
NEVERBALL_SITE = https://github.com/Neverball/neverball
NEVERBALL_SITE_METHOD = git
NEVERBALL_LICENSE = GPL-2.0+
NEVERBALL_LICENSE_FILES = COPYING

NEVERBALL_DEPENDENCIES = sdl2 sdl2_ttf libvorbis libogg libpng jpeg

NEVERBALL_BUILD_OPTS = \
	CC="$(TARGET_CC)" \
	CFLAGS="$(TARGET_CFLAGS)" \
	LDFLAGS="$(TARGET_LDFLAGS) -lpng -ljpeg" \
	ENABLE_NLS=0 \
	ENABLE_FETCH= \
	ENABLE_RADIANT_CONSOLE=0 \
	BUILD=release

ifeq ($(BR2_PACKAGE_HAS_LIBGLES),y)
NEVERBALL_DEPENDENCIES += libgles
NEVERBALL_BUILD_OPTS += ENABLE_OPENGLES=1
else
NEVERBALL_DEPENDENCIES += libgl
endif

define NEVERBALL_FIX_SDLCONFIG
	sed -i 's|sdl2-config --cflags|$(PKG_CONFIG_HOST_BINARY) sdl2 --cflags|g' $(@D)/Makefile
	sed -i 's|sdl2-config --libs|$(PKG_CONFIG_HOST_BINARY) sdl2 --libs|g' $(@D)/Makefile
	sed -i 's|libpng-config --cflags|$(PKG_CONFIG_HOST_BINARY) libpng --cflags|g' $(@D)/Makefile
	sed -i 's|libpng-config --ldflags|$(PKG_CONFIG_HOST_BINARY) libpng --libs|g' $(@D)/Makefile
endef
NEVERBALL_POST_PATCH_HOOKS += NEVERBALL_FIX_SDLCONFIG

define NEVERBALL_BUILD_CMDS
	$(TARGET_MAKE_ENV) $(MAKE) -C $(@D) $(NEVERBALL_BUILD_OPTS) -j$(PARALLEL_JOBS)
endef

define NEVERBALL_INSTALL_TARGET_CMDS
	$(INSTALL) -D -m 0755 $(@D)/neverball $(TARGET_DIR)/usr/bin/neverball
	$(INSTALL) -D -m 0755 $(@D)/neverputt $(TARGET_DIR)/usr/bin/neverputt
	mkdir -p $(TARGET_DIR)/usr/share/neverball
	cp -r $(@D)/data $(TARGET_DIR)/usr/share/neverball/
endef

$(eval $(generic-package))
