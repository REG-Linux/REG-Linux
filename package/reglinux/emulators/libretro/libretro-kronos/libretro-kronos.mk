################################################################################
#
# libretro-kronos
#
################################################################################

LIBRETRO_KRONOS_VERSION = 2.7.0_official_release
LIBRETRO_KRONOS_SITE = $(call github,FCare,kronos,$(LIBRETRO_KRONOS_VERSION))
LIBRETRO_KRONOS_LICENSE = BSD-3-Clause

LIBRETRO_KRONOS_PLATFORM = $(LIBRETRO_PLATFORM)

ifeq ($(BR2_PACKAGE_HAS_LIBGL),y)
LIBRETRO_KRONOS_DEPENDENCIES += libgl
else ifeq ($(BR2_PACKAGE_HAS_LIBGLES),y)
LIBRETRO_KRONOS_DEPENDENCIES += libgles
LIBRETRO_KRONOS_EXTRA_ARGS += FORCE_GLES=1
endif

ifeq ($(BR2_PACKAGE_SYSTEM_TARGET_XU4),y)
LIBRETRO_KRONOS_PLATFORM = odroid
LIBRETRO_KRONOS_EXTRA_ARGS += BOARD=ODROID-XU4

else ifeq ($(BR2_PACKAGE_SYSTEM_TARGET_S922X),y)
LIBRETRO_KRONOS_PLATFORM = odroid-n2

else ifeq ($(BR2_PACKAGE_SYSTEM_TARGET_RK3399),y)
LIBRETRO_KRONOS_PLATFORM = rockpro64

else ifeq ($(BR2_PACKAGE_SYSTEM_TARGET_S905GEN3),y)
LIBRETRO_KRONOS_PLATFORM = odroid-c4

# Unoptimized yet
else ifeq ($(BR2_aarch64),y)
LIBRETRO_KRONOS_PLATFORM = arm64
endif

define LIBRETRO_KRONOS_BUILD_CMDS
	$(MAKE) -C $(@D)/yabause/src/libretro -f Makefile generate-files && \
	$(TARGET_CONFIGURE_OPTS) $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C \
	    $(@D)/yabause/src/libretro -f Makefile \
		platform="$(LIBRETRO_KRONOS_PLATFORM)" $(LIBRETRO_KRONOS_EXTRA_ARGS)
endef

define LIBRETRO_KRONOS_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/yabause/src/libretro/kronos_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/kronos_libretro.so
endef

$(eval $(generic-package))
