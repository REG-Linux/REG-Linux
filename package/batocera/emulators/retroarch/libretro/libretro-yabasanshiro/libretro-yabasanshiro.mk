################################################################################
#
# libretro-yabasanshiro
#
################################################################################
# Version: Commits on May 23, 2024
# Need to use this branch : https://github.com/libretro/yabause/tree/yabasanshiro
LIBRETRO_YABASANSHIRO_BRANCH = yabasanshiro
LIBRETRO_YABASANSHIRO_VERSION = 39535a6abcad5abf9f71c8b2a7975f005ee12ed6
LIBRETRO_YABASANSHIRO_SITE = $(call github,libretro,yabause,$(LIBRETRO_YABASANSHIRO_VERSION))
LIBRETRO_YABASANSHIRO_LICENSE = GPLv2

LIBRETRO_YABASANSHIRO_PLATFORM = $(LIBRETRO_PLATFORM)
LIBRETRO_YABASANSHIRO_TARGET_LDFLAGS = $(TARGET_LDFLAGS)

ifeq ($(BR2_aarch64),y)
LIBRETRO_YABASANSHIRO_PLATFORM = unix arm64

else ifeq ($(BR2_arm),y)
LIBRETRO_YABASANSHIRO_PLATFORM = unix armv

else ifeq ($(BR2_x86_64)$(BR2_x86_x86_64_v3),y)
LIBRETRO_YABASANSHIRO_PLATFORM = unix
LIBRETRO_YABASANSHIRO_EXTRA_ARGS = FORCE_GLES=0
LIBRETRO_YABASANSHIRO_TARGET_LDFLAGS += -shared -Wl,--no-undefined -pthread -lGL

else ifeq ($(BR2_PACKAGE_HAS_LIBMALI),y)
LIBRETRO_YABASANSHIRO_DEPENDENCIES += libmali
LIBRETRO_YABASANSHIRO_TARGET_LDFLAGS += -lmali
endif

define LIBRETRO_YABASANSHIRO_BUILD_CMDS
	$(TARGET_CONFIGURE_OPTS) LDFLAGS="$(LIBRETRO_YABASANSHIRO_TARGET_LDFLAGS)" $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" \
		-C $(@D)/yabause/src/libretro -f Makefile platform="$(LIBRETRO_YABASANSHIRO_PLATFORM)" $(LIBRETRO_YABASANSHIRO_EXTRA_ARGS) \
        GIT_VERSION="-$(shell echo $(LIBRETRO_YABASANSHIRO_VERSION) | cut -c 1-7)"
endef

define LIBRETRO_YABASANSHIRO_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/yabause/src/libretro/yabasanshiro_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/yabasanshiro_libretro.so
endef

$(eval $(generic-package))
