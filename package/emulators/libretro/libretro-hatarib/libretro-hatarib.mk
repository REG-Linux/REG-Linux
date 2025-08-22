################################################################################
#
# libretro-hatarib
#
################################################################################

# Commits on Feb 9, 2025
LIBRETRO_HATARIB_VERSION = 162d2ed3ee40d8ea394607e7f886a084b660ad5f
LIBRETRO_HATARIB_SITE = https://github.com/bbbradsmith/hatariB
LIBRETRO_HATARIB_SITE_METHOD=git
LIBRETRO_HATARIB_LICENSE = GPLv2
LIBRETRO_HATARIB_DEPENDENCIES = libcapsimage libpng zlib sdl2

LIBRETRO_HATARIB_GIT_SUBMODULES = YES

LIBRETRO_HATARIB_CC_FLAGS = -fPIC -D__LIBRETRO__ -DSHORTHASH="\"reglinux\"" -I$(@D)/hatari -I$(@D)/hatari/build -I$(STAGING_DIR)/usr/include/SDL2 -L$(STAGING_DIR)/usr/lib -lSDL2 -I$(STAGING_DIR)/usr/include -lz

LIBRETRO_HATARIB_CONF_ENV += \
    SHORTHASH='"$(shell echo $(LIBRETRO_HATARIB_VERSION) | cut -c 1-7)"' \
	SDL2_INCLUDE="$(STAGING_DIR)/usr/include/SDL2" \
	SDL2_LIB="$(STAGING_DIR)/usr/lib" \
	SDL2_LINK="$(STAGING_DIR)/usr/lib/libSDL2.so" \
	ZLIB_INCLUDE="$(STAGING_DIR)/usr/include" \
	ZLIB_LIB="$(STAGING_DIR)/usr/lib" \
	ZLIB_LINK="$(STAGING_DIR)/usr/lib/libz.so" \
	CFLAGS="$(TARGET_CFLAGS) $(LIBRETRO_HATARIB_CC_FLAGS)" \
	CC="$(TARGET_CC)" \
	AR="$(TARGET_AR)" \
	RANLIB="$(TARGET_RANLIB)"

define LIBRETRO_HATARIB_BUILD_CMDS
	cd $(@D) && $(MAKE) -f makefile $(LIBRETRO_HATARIB_CONF_ENV)
endef

define LIBRETRO_HATARIB_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/build/hatarib.so \
		$(TARGET_DIR)/usr/lib/libretro/hatarib_libretro.so
endef

$(eval $(generic-package))
