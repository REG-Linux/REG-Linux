################################################################################
#
# ccleste — Celeste Classic (C source port of PICO-8 Celeste)
#
################################################################################

CCLESTE_VERSION = v1.4.0
CCLESTE_SITE = https://github.com/lemon32767/ccleste
CCLESTE_SITE_METHOD = git
CCLESTE_LICENSE = Unlicensed (public distribution)

CCLESTE_DEPENDENCIES = sdl2 sdl2_mixer

define CCLESTE_BUILD_CMDS
	$(TARGET_MAKE_ENV) $(MAKE) -C $(@D) \
		CC="$(TARGET_CC)" \
		CFLAGS="$(TARGET_CFLAGS) $$($(PKG_CONFIG_HOST_BINARY) sdl2 --cflags)" \
		LDFLAGS="$(TARGET_LDFLAGS) $$($(PKG_CONFIG_HOST_BINARY) sdl2 --libs) -lSDL2_mixer -lm"
endef

define CCLESTE_INSTALL_TARGET_CMDS
	$(INSTALL) -D -m 0755 $(@D)/ccleste $(TARGET_DIR)/usr/bin/ccleste
endef

$(eval $(generic-package))
