################################################################################
#
# yatka — Tetris implementation (SDL 1.2)
#
################################################################################

YATKA_VERSION = v0.9
YATKA_SITE = https://github.com/szymor/yatka
YATKA_SITE_METHOD = git
YATKA_LICENSE = GPL-2.0
YATKA_LICENSE_FILES = COPYING

YATKA_DEPENDENCIES = sdl sdl_image sdl_mixer sdl_ttf

define YATKA_BUILD_CMDS
	$(TARGET_MAKE_ENV) $(MAKE) -C $(@D) \
		CC="$(TARGET_CC)" \
		CFLAGS="$(TARGET_CFLAGS) -Iinc $$($(PKG_CONFIG_HOST_BINARY) sdl SDL_image SDL_ttf SDL_mixer --cflags)" \
		LDFLAGS="$(TARGET_LDFLAGS) $$($(PKG_CONFIG_HOST_BINARY) sdl SDL_image SDL_ttf SDL_mixer --libs) -lm"
endef

define YATKA_INSTALL_TARGET_CMDS
	$(INSTALL) -D -m 0755 $(@D)/yatka $(TARGET_DIR)/usr/bin/yatka
	mkdir -p $(TARGET_DIR)/usr/share/yatka
	cp -r $(@D)/res $(TARGET_DIR)/usr/share/yatka/
endef

$(eval $(generic-package))
