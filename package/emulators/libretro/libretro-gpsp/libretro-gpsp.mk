
################################################################################
#
# libretro-gpsp
#
################################################################################
# Version: Commits on Aug 25, 2026
LIBRETRO_GPSP_VERSION = 8d268a6bb2cd799f8f2791ebb544a7ef550cfc6f
LIBRETRO_GPSP_SITE = $(call github,libretro,gpsp,$(LIBRETRO_GPSP_VERSION))
LIBRETRO_GPSP_LICENSE = GPLv2

LIBRETRO_GPSP_PLATFORM = unix

ifeq ($(BR2_PACKAGE_SYSTEM_TARGET_BCM2835),y)
LIBRETRO_GPSP_PLATFORM = rpi1
else ifeq ($(BR2_PACKAGE_SYSTEM_TARGET_JZ4770),y)
LIBRETRO_GPSP_PLATFORM = jz4770
else ifeq ($(BR2_cortex_a7),y)
LIBRETRO_GPSP_PLATFORM = classic_armv7_a7
endif

define LIBRETRO_GPSP_BUILD_CMDS
	$(TARGET_CONFIGURE_OPTS) $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" \
	    -C $(@D) platform=$(LIBRETRO_GPSP_PLATFORM) \
        GIT_VERSION="-$(shell echo $(LIBRETRO_GPSP_VERSION) | cut -c 1-7)"
endef

define LIBRETRO_GPSP_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/gpsp_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/gpsp_libretro.so
endef

$(eval $(generic-package))
