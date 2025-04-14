################################################################################
#
# libretro-puae2021
#
################################################################################
# Version: Commits on Mar 27, 2025
LIBRETRO_PUAE2021_VERSION = dde80f385c57e06b73810abf79f2d935312467dc
LIBRETRO_PUAE2021_SITE = $(call github,libretro,libretro-uae,$(LIBRETRO_PUAE2021_VERSION))
LIBRETRO_PUAE2021_LICENSE = GPLv2

LIBRETRO_PUAE2021_PLATFORM=$(LIBRETRO_PLATFORM)

ifeq ($(BR2_PACKAGE_SYSTEM_TARGET_BCM2835),y)
LIBRETRO_PUAE2021_PLATFORM = rpi1
else ifeq ($(BR2_PACKAGE_SYSTEM_TARGET_BCM2836),y)
LIBRETRO_PUAE2021_PLATFORM = rpi2
else ifeq ($(BR2_PACKAGE_SYSTEM_TARGET_BCM2837),y)
LIBRETRO_PUAE2021_PLATFORM = rpi3_64
else ifeq ($(BR2_PACKAGE_SYSTEM_TARGET_BCM2711),y)
LIBRETRO_PUAE2021_PLATFORM = rpi4
else ifeq ($(BR2_PACKAGE_SYSTEM_TARGET_BCM2712),y)
LIBRETRO_PUAE2021_PLATFORM = rpi5
endif

define LIBRETRO_PUAE2021_BUILD_CMDS
	$(TARGET_CONFIGURE_OPTS) $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C $(@D)/ -f Makefile platform="$(LIBRETRO_PUAE2021_PLATFORM)" \
        GIT_VERSION="-$(shell echo $(LIBRETRO_PUAE2021_VERSION) | cut -c 1-7)"
endef

define LIBRETRO_PUAE2021_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/puae2021_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/puae2021_libretro.so
endef

$(eval $(generic-package))
