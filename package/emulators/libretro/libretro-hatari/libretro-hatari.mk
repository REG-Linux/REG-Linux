################################################################################
#
# libretro-hatari
#
################################################################################
# Version: Commits on Sep 3, 2026 (moving fast in development)
LIBRETRO_HATARI_VERSION = 7fd34ccf34c6ea12b7f2b960b2f167d7f251892d
LIBRETRO_HATARI_SITE = $(call github,libretro,hatari,$(LIBRETRO_HATARI_VERSION))
LIBRETRO_HATARI_DEPENDENCIES = libcapsimage zlib sdl2
LIBRETRO_HATARI_LICENSE = GPLv3

LIBRETRO_HATARI_PLATFORM = $(LIBRETRO_PLATFORM)

ifeq ($(BR2_PACKAGE_SYSTEM_TARGET_BCM2835),y)
LIBRETRO_HATARI_PLATFORM = rpi1
else ifeq ($(BR2_PACKAGE_SYSTEM_TARGET_BCM2836),y)
LIBRETRO_HATARI_PLATFORM = rpi2
else ifeq ($(BR2_PACKAGE_SYSTEM_TARGET_BCM2837),y)
LIBRETRO_HATARI_PLATFORM = rpi3_64
else ifeq ($(BR2_PACKAGE_SYSTEM_TARGET_BCM2711),y)
LIBRETRO_HATARI_PLATFORM = rpi4
else ifeq ($(BR2_PACKAGE_SYSTEM_TARGET_BCM2712),y)
LIBRETRO_HATARI_PLATFORM = rpi5
else ifeq ($(BR2_PACKAGE_SYSTEM_TARGET_S812),y)
LIBRETRO_HATARI_PLATFORM = armv
else ifeq ($(BR2_aarch64),y)
LIBRETRO_HATARI_PLATFORM = unix
endif

LIBRETRO_HATARI_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release
LIBRETRO_HATARI_CONF_OPTS += -DBUILD_SHARED_LIBS=OFF
LIBRETRO_HATARI_CONF_OPTS += -DBUILD_STATIC_LIBS=ON
LIBRETRO_HATARI_CONF_OPTS += -DCAPSIMAGE_INCLUDE_DIR="$(STAGING_DIR)/usr/include"
LIBRETRO_HATARI_CONF_OPTS += -DENABLE_MAN_PAGES=OFF
LIBRETRO_HATARI_CONF_OPTS += -DENABLE_OSX_BUNDLE=OFF
LIBRETRO_HATARI_CONF_OPTS += -DENABLE_LIBRETRO=ON
LIBRETRO_HATARI_CONF_OPTS += -DENABLE_HATARI=OFF
LIBRETRO_HATARI_CONF_OPTS += -DENABLE_TOOLS=OFF

# ARM NEON optimizations for ARM architectures
ifeq ($(BR2_arm),y)
ifeq ($(BR2_ARM_FPU_NEON),y)
HATARI_CONF_OPTS += -DCMAKE_C_FLAGS="$(TARGET_CFLAGS) -mfpu=neon -mfloat-abi=hard"
endif
endif
ifeq ($(BR2_aarch64),y)
HATARI_CONF_OPTS += -DCMAKE_C_FLAGS="$(TARGET_CFLAGS) -march=armv8-a+simd"
endif

define LIBRETRO_HATARI_INSTALL_TARGET_CMDS
       $(INSTALL) -D $(@D)/src/hatari_libretro.so \
               $(TARGET_DIR)/usr/lib/libretro/hatari_libretro.so
       $(INSTALL) -D $(@D)/share/libretro/info/libretro-hatari.info \
               $(TARGET_DIR)/usr/share/libretro/hatari_libretro.info
endef

$(eval $(cmake-package))
