################################################################################
#
# libretro-geargrafx
#
################################################################################
# Version: Release on Feb 1, 2026
LIBRETRO_GEARGRAFX_VERSION = 1.6.11
LIBRETRO_GEARGRAFX_SITE = $(call github,drhelius,Geargrafx,$(LIBRETRO_GEARGRAFX_VERSION))
LIBRETRO_GEARGRAFX_LICENSE = GPLv3

LIBRETRO_GEARGRAFX_PLATFORM = $(LIBRETRO_PLATFORM)

ifeq ($(BR2_PACKAGE_SYSTEM_TARGET_BCM2835),y)
LIBRETRO_GEARGRAFX_PLATFORM += rpi1

else ifeq ($(BR2_cortex_a7),y)
LIBRETRO_GEARGRAFX_PLATFORM += classic_armv7_a7

else ifeq ($(BR2_cortex_a53),y)
LIBRETRO_GEARGRAFX_PLATFORM += rpi3

else ifeq ($(BR2_cortex_a72),y)
LIBRETRO_GEARGRAFX_PLATFORM += rpi4

else ifeq ($(BR2_cortex_a76),y)
LIBRETRO_GEARGRAFX_PLATFORM += rpi5

else ifeq ($(BR2_PACKAGE_SYSTEM_TARGET_S922X),y)
LIBRETRO_GEARGRAFX_PLATFORM += s922x

else ifeq ($(BR2_PACKAGE_SYSTEM_TARGET_RK3326),y)
LIBRETRO_GEARGRAFX_PLATFORM += rk3326

else ifeq ($(BR2_PACKAGE_SYSTEM_TARGET_RK3399),y)
LIBRETRO_GEARGRAFX_PLATFORM += rk3399

else ifeq ($(BR2_cortex_a55),y)
LIBRETRO_GEARGRAFX_PLATFORM += rk3568

else ifeq ($(BR2_PACKAGE_SYSTEM_TARGET_RK3588),y)
LIBRETRO_GEARGRAFX_PLATFORM += rk3588
endif

define LIBRETRO_GEARGRAFX_BUILD_CMDS
	$(TARGET_CONFIGURE_OPTS) $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C \
        $(@D)/platforms/libretro -f Makefile platform="$(LIBRETRO_GEARGRAFX_PLATFORM)"
endef

define LIBRETRO_GEARGRAFX_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/usr/lib/libretro
	$(INSTALL) -D $(@D)/platforms/libretro/geargrafx_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/geargrafx_libretro.so
	mkdir -p $(TARGET_DIR)/usr/share/libretro/info
	$(INSTALL) -D $(@D)/platforms/libretro/geargrafx_libretro.info \
		$(TARGET_DIR)/usr/share/libretro/info/
endef

$(eval $(generic-package))
