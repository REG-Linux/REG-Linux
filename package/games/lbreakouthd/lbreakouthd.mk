################################################################################
#
# lbreakouthd
#
################################################################################

LBREAKOUTHD_VERSION = 1.2
LBREAKOUTHD_SOURCE = lbreakouthd-$(LBREAKOUTHD_VERSION).tar.gz
LBREAKOUTHD_SITE = https://sourceforge.net/projects/lgames/files/lbreakouthd
LBREAKOUTHD_LICENSE = GPL-2.0+
LBREAKOUTHD_LICENSE_FILES = COPYING

LBREAKOUTHD_DEPENDENCIES = sdl2 sdl2_mixer sdl2_image sdl2_ttf libpng $(TARGET_NLS_DEPENDENCIES)

LBREAKOUTHD_CONF_OPTS = -with-sysroot=$(STAGING_DIR)

ifeq ($(BR2_TOOLCHAIN_USES_MUSL),y)
LBREAKOUTHD_CONF_OPTS += ac_cv_func_malloc_0_nonnull=yes
LBREAKOUTHD_CONF_OPTS += ac_cv_func_realloc_0_nonnull=yes
endif

LBREAKOUTHD_CONF_ENV = \
	SYSROOT=$(STAGING_DIR) \
	PREFIX="/$(BR2_ARCH)/host/$(BR2_ARCH)-buildroot-linux-gnu/sysroot/" \
	SDL2_CONFIG="$(STAGING_DIR)/usr/bin/sdl2-config" \
    	CFLAGS="$(TARGET_CFLAGS) $$($(PKG_CONFIG_HOST_BINARY) --cflags sdl2)" \
    	LDFLAGS="$(TARGET_LDFLAGS) $$($(PKG_CONFIG_HOST_BINARY) --libs sdl2)" \
	LIBS=$(TARGET_NLS_LIBS)

$(eval $(autotools-package))
