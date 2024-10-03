################################################################################
#
# libretro-genesisplusgx
#
################################################################################
# Version: Commits on Jul 20, 2024
LIBRETRO_GENESISPLUSGX_VERSION = 2fd18851754e715bd55e7040aaace2590ac0d8cb
LIBRETRO_GENESISPLUSGX_SITE = $(call github,ekeeke,Genesis-Plus-GX,$(LIBRETRO_GENESISPLUSGX_VERSION))
LIBRETRO_GENESISPLUSGX_LICENSE = Non-commercial

LIBRETRO_GENESISPLUSGX_PLATFORM = $(LIBRETRO_PLATFORM)

ifeq ($(BR2_cortex_a7),y)
LIBRETRO_GENESISPLUSGX_PLATFORM += rpi2

else ifeq ($(BR2_cortex_a53),y)
LIBRETRO_GENESISPLUSGX_PLATFORM += rpi3_64

else ifeq ($(BR2_cortex_a72),y)
LIBRETRO_GENESISPLUSGX_PLATFORM += rpi4

else ifeq ($(BR2_cortex_a76),y)
LIBRETRO_GENESISPLUSGX_PLATFORM += rpi5

else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_S922X),y)
LIBRETRO_GENESISPLUSGX_PLATFORM += CortexA73_G12B

else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RK3326),y)
LIBRETRO_GENESISPLUSGX_PLATFORM += classic_armv8_a35

else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RK3399),y)
LIBRETRO_GENESISPLUSGX_PLATFORM += rk3399

else ifeq ($(BR2_cortex_a55),y)
LIBRETRO_GENESISPLUSGX_PLATFORM += rk3568

else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RK3588),y)
LIBRETRO_GENESISPLUSGX_PLATFORM += rk3588

else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_ODIN),y)
LIBRETRO_GENESISPLUSGX_PLATFORM += odin
endif

define LIBRETRO_GENESISPLUSGX_BUILD_CMDS
	$(TARGET_CONFIGURE_OPTS) $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C $(@D) -f Makefile.libretro platform="$(LIBRETRO_GENESISPLUSGX_PLATFORM)" \
        GIT_VERSION="-$(shell echo $(LIBRETRO_GENESISPLUSGX_VERSION) | cut -c 1-7)"
endef

define LIBRETRO_GENESISPLUSGX_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/genesis_plus_gx_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/genesisplusgx_libretro.so
endef

$(eval $(generic-package))
