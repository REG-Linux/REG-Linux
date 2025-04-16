################################################################################
#
# libretro-nxengine
#
################################################################################
# Version: Commits on Oct 21, 2024
LIBRETRO_NXENGINE_VERSION = 9adc032a5f6aa913d71d22042bb72cb11cf0f4a2
LIBRETRO_NXENGINE_SITE = $(call github,libretro,nxengine-libretro,$(LIBRETRO_NXENGINE_VERSION))
LIBRETRO_NXENGINE_LICENSE = GPLv3

LIBRETRO_NXENGINE_PLATFORM = $(LIBRETRO_PLATFORM)

ifeq ($(BR2_PACKAGE_SYSTEM_TARGET_S812),y)
LIBRETRO_NXENGINE_PLATFORM = armv
else ifeq ($(BR2_PACKAGE_SYSTEM_TARGET_BCM2835),y)
LIBRETRO_NXENGINE_PLATFORM = rpi1
else ifeq ($(BR2_PACKAGE_SYSTEM_TARGET_BCM2836),y)
LIBRETRO_NXENGINE_PLATFORM = rpi2
else ifeq ($(BR2_PACKAGE_SYSTEM_TARGET_BCM2837),y)
LIBRETRO_NXENGINE_PLATFORM = rpi3_64
else ifeq ($(BR2_PACKAGE_SYSTEM_TARGET_BCM2711),y)
LIBRETRO_NXENGINE_PLATFORM = rpi4_64
else ifeq ($(BR2_PACKAGE_SYSTEM_TARGET_BCM2712),y)
LIBRETRO_NXENGINE_PLATFORM = rpi5_64
else ifeq ($(BR2_aarch64),y)
LIBRETRO_NXENGINE_PLATFORM = unix
endif

define LIBRETRO_NXENGINE_BUILD_CMDS
	$(TARGET_CONFIGURE_OPTS) $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C $(@D)/ -f Makefile platform="$(LIBRETRO_NXENGINE_PLATFORM)"
endef

define LIBRETRO_NXENGINE_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/nxengine_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/nxengine_libretro.so
endef

$(eval $(generic-package))
