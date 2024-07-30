################################################################################
#
# libretro-puae
#
################################################################################
# Version: Commits on May 25, 2024
LIBRETRO_PUAE_VERSION = 4493a194dd42e593914c26952ee8cb4ba750f596
LIBRETRO_PUAE_SITE = $(call github,libretro,libretro-uae,$(LIBRETRO_PUAE_VERSION))
LIBRETRO_PUAE__LICENSE = GPLv2

LIBRETRO_PUAE_PLATFORM=$(LIBRETRO_PLATFORM)

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_BCM2835),y)
LIBRETRO_PUAE_PLATFORM = rpi1
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_BCM2836),y)
LIBRETRO_PUAE_PLATFORM = rpi2
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_BCM2837),y)
LIBRETRO_PUAE_PLATFORM = rpi3_64
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_BCM2711),y)
LIBRETRO_PUAE_PLATFORM = rpi4
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_BCM2712),y)
LIBRETRO_PUAE_PLATFORM = rpi5
else ifeq ($(BR2_cortex_a7),y)
LIBRETRO_PUAE_PLATFORM = classic_armv7_a7
endif

define LIBRETRO_PUAE_BUILD_CMDS
	$(TARGET_CONFIGURE_OPTS) $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" \
	    -C $(@D)/ -f Makefile platform="$(LIBRETRO_PUAE_PLATFORM)" \
        GIT_VERSION="-$(shell echo $(LIBRETRO_PUAE_VERSION) | cut -c 1-7)"
endef

define LIBRETRO_PUAE_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/puae_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/puae_libretro.so
endef

$(eval $(generic-package))
