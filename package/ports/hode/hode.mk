################################################################################
#
# hode — Heart of Darkness engine reimplementation (Gregory Montoir)
#
################################################################################

HODE_VERSION = 0.2.9f
HODE_SITE = https://github.com/cyxx/hode
HODE_SITE_METHOD = git
HODE_LICENSE = GPL-2.0

HODE_DEPENDENCIES = sdl2

define HODE_BUILD_CMDS
	$(TARGET_MAKE_ENV) $(MAKE) -C $(@D) \
		CXX="$(TARGET_CXX)" \
		CXXFLAGS="$(TARGET_CFLAGS) $$($(PKG_CONFIG_HOST_BINARY) sdl2 --cflags)" \
		LDFLAGS="$(TARGET_LDFLAGS) $$($(PKG_CONFIG_HOST_BINARY) sdl2 --libs)"
endef

define HODE_INSTALL_TARGET_CMDS
	$(INSTALL) -D -m 0755 $(@D)/hode $(TARGET_DIR)/usr/bin/hode
endef

$(eval $(generic-package))
