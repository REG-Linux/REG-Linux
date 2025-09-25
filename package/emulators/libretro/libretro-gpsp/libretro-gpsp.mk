
################################################################################
#
# libretro-gpsp
#
################################################################################
# Version: Commits on Sep 17, 2025
LIBRETRO_GPSP_VERSION = a545aafaf4e654a488f4588f4f302d8413a58066
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
