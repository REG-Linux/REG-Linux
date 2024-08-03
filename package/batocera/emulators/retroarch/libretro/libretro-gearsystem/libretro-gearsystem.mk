################################################################################
#
# libretro-gearsystem
#
################################################################################
# Version: Commits on Mar 3, 2024
LIBRETRO_GEARSYSTEM_VERSION = 3.5.0
LIBRETRO_GEARSYSTEM_SITE = $(call github,drhelius,Gearsystem,$(LIBRETRO_GEARSYSTEM_VERSION))
LIBRETRO_GEARSYSTEM_LICENSE = GPLv3

LIBRETRO_GEARSYSTEM_PLATFORM = $(LIBRETRO_PLATFORM)

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_BCM2835),y)
LIBRETRO_GEARSYSTEM_PLATFORM += rpi1

else ifeq ($(BR2_cortex_a7),y)
LIBRETRO_GEARSYSTEM_PLATFORM += classic_armv7_a7

else ifeq ($(BR2_cortex_a53),y)
LIBRETRO_GEARSYSTEM_PLATFORM += rpi3

else ifeq ($(BR2_cortex_a72),y)
LIBRETRO_GEARSYSTEM_PLATFORM += rpi4

else ifeq ($(BR2_cortex_a76),y)
LIBRETRO_GEARSYSTEM_PLATFORM += rpi5

else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_S922X),y)
LIBRETRO_GEARSYSTEM_PLATFORM += s922x

else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RK3326),y)
LIBRETRO_GEARSYSTEM_PLATFORM += rk3326

else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RK3399),y)
LIBRETRO_GEARSYSTEM_PLATFORM += rk3399

else ifeq ($(BR2_cortex_a55),y)
LIBRETRO_GEARSYSTEM_PLATFORM += rk3568

else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RK3588),y)
LIBRETRO_GEARSYSTEM_PLATFORM += rk3588
endif

define LIBRETRO_GEARSYSTEM_BUILD_CMDS
	$(TARGET_CONFIGURE_OPTS) $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C \
        $(@D)/platforms/libretro -f Makefile platform="$(LIBRETRO_GEARSYSTEM_PLATFORM)"
endef

define LIBRETRO_GEARSYSTEM_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/platforms/libretro/gearsystem_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/gearsystem_libretro.so
endef

$(eval $(generic-package))
