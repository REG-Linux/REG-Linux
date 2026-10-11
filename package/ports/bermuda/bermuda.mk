################################################################################
#
# bermuda — Bermuda Syndrome engine reimplementation (Gregory Montoir)
#
################################################################################

BERMUDA_VERSION = 0.1.7
BERMUDA_SITE = https://github.com/cyxx/bermuda
BERMUDA_SITE_METHOD = git
BERMUDA_LICENSE = GPL-2.0

BERMUDA_DEPENDENCIES = sdl2 sdl2_mixer libvorbis libogg zlib

define BERMUDA_BUILD_CMDS
	$(TARGET_MAKE_ENV) $(MAKE) -C $(@D) \
		CXX="$(TARGET_CXX)" \
		SDL_CFLAGS="$$($(PKG_CONFIG_HOST_BINARY) sdl2 --cflags)" \
		SDL_LIBS="$$($(PKG_CONFIG_HOST_BINARY) sdl2 --libs) -lSDL2_mixer"
endef

define BERMUDA_INSTALL_TARGET_CMDS
	$(INSTALL) -D -m 0755 $(@D)/bs $(TARGET_DIR)/usr/bin/bermuda
endef

$(eval $(generic-package))
