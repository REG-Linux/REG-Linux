
################################################################################
#
# libretro-geolith
#
################################################################################
# Version: Commits on May 14, 2024
LIBRETRO_GEOLITH_VERSION = 4d9692a48bbb375556527bd1aade29b1de9e497e
LIBRETRO_GEOLITH_SITE = https://github.com/libretro/geolith-libretro.git
LIBRETRO_GEOLITH_SITE_METHOD = git
LIBRETRO_GEOLITH_LICENSE = BSD

LIBRETRO_GEOLITH_PLATFORM = $(LIBRETRO_PLATFORM)

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_BCM2835),y)
LIBRETRO_GEOLITH_PLATFORM = rpi1
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_BCM2836),y)
LIBRETRO_GEOLITH_PLATFORM = rpi2
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_BCM2837),y)
LIBRETRO_GEOLITH_PLATFORM = rpi3_64
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_BCM2711),y)
LIBRETRO_GEOLITH_PLATFORM = rpi4
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_BCM2712),y)
LIBRETRO_GEOLITH_PLATFORM = rpi5
else
LIBRETRO_GEOLITH_PLATFORM = unix
endif

define LIBRETRO_GEOLITH_BUILD_CMDS
	$(TARGET_CONFIGURE_OPTS) $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C $(@D)/libretro \
	    -f Makefile platform="$(LIBRETRO_GEOLITH_PLATFORM)" \
#        GIT_VERSION="-$(shell echo $(LIBRETRO_GEOLITH_VERSION) | cut -c 1-7)"
endef

define LIBRETRO_GEOLITH_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/libretro/geolith_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/geolith_libretro.so
endef

$(eval $(generic-package))
