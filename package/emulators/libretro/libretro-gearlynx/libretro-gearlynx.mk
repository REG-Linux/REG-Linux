################################################################################
#
# libretro-gearlynx
#
################################################################################
# Version: Release on Jan 24, 2026
LIBRETRO_GEARLYNX_VERSION = 1.0.0
LIBRETRO_GEARLYNX_SITE = $(call github,drhelius,Gearlynx,$(LIBRETRO_GEARLYNX_VERSION))
LIBRETRO_GEARLYNX_LICENSE = GPLv3

LIBRETRO_GEARLYNX_PLATFORM = $(LIBRETRO_PLATFORM)

ifeq ($(BR2_PACKAGE_SYSTEM_TARGET_BCM2835),y)
LIBRETRO_GEARLYNX_PLATFORM += rpi1

else ifeq ($(BR2_cortex_a7),y)
LIBRETRO_GEARLYNX_PLATFORM += classic_armv7_a7

else ifeq ($(BR2_cortex_a53),y)
LIBRETRO_GEARLYNX_PLATFORM += rpi3

else ifeq ($(BR2_cortex_a72),y)
LIBRETRO_GEARLYNX_PLATFORM += rpi4

else ifeq ($(BR2_cortex_a76),y)
LIBRETRO_GEARLYNX_PLATFORM += rpi5

else ifeq ($(BR2_PACKAGE_SYSTEM_TARGET_S922X),y)
LIBRETRO_GEARLYNX_PLATFORM += s922x

else ifeq ($(BR2_PACKAGE_SYSTEM_TARGET_RK3326),y)
LIBRETRO_GEARLYNX_PLATFORM += rk3326

else ifeq ($(BR2_PACKAGE_SYSTEM_TARGET_RK3399),y)
LIBRETRO_GEARLYNX_PLATFORM += rk3399

else ifeq ($(BR2_cortex_a55),y)
LIBRETRO_GEARLYNX_PLATFORM += rk3568

else ifeq ($(BR2_PACKAGE_SYSTEM_TARGET_RK3588),y)
LIBRETRO_GEARLYNX_PLATFORM += rk3588
endif

define LIBRETRO_GEARLYNX_BUILD_CMDS
	$(TARGET_CONFIGURE_OPTS) $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C \
        $(@D)/platforms/libretro -f Makefile platform="$(LIBRETRO_GEARLYNX_PLATFORM)"
endef

define LIBRETRO_GEARLYNX_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/platforms/libretro/gearlynx_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/gearlynx_libretro.so
endef

$(eval $(generic-package))
