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

# GL API selection
ifeq ($(BR2_PACKAGE_HAS_LIBGL),y)
LIBRETRO_YABASANSHIRO_EXTRA_ARGS += FORCE_GLES=0
LIBRETRO_YABASANSHIRO_TARGET_LDFLAGS += -lGL
LIBRETRO_YABASANSHIRO_DEPENDENCIES += libgl
else
LIBRETRO_YABASANSHIRO_EXTRA_ARGS += FORCE_GLES=1
LIBRETRO_YABASANSHIRO_DEPENDENCIES += libgles
endif

# Architecture-dependent options
ifeq ($(BR2_aarch64),y)
LIBRETRO_YABASANSHIRO_PLATFORM = unix arm64
LIBRETRO_YABASANSHIRO_EXTRA_ARGS += HAVE_SSE=0 USE_AARCH64_DRC=1 DYNAREC_DEVMIYAX=1
LIBRETRO_YABASANSHIRO_TARGET_CFLAGS += -DAARCH64
# missing -march -mcpu -mtune
else ifeq ($(BR2_arm),y)
LIBRETRO_YABASANSHIRO_PLATFORM = unix armv
LIBRETRO_YABASANSHIRO_EXTRA_ARGS += HAVE_SSE=0 HAVE_NEON=1 USE_ARM_DRC=1 DYNAREC_DEVMIYAX=1
LIBRETRO_YABASANSHIRO_TARGET_CFLAGS += -mfloat-abi=hard
# missing -march -mcpu -mfpu - mtune -mvectorize-with-neon-quad
else ifeq ($(BR2_x86_64)$(BR2_x86_x86_64_v3),y)
LIBRETRO_YABASANSHIRO_PLATFORM = unix
#LIBRETRO_YABASANSHIRO_EXTRA_ARGS += HAVE_SSE=1 HAVE_NEON=0 DYNAREC_DEVMIYAX=1
LIBRETRO_YABASANSHIRO_TARGET_LDFLAGS += -shared -Wl,--no-undefined -pthread -lGL
endif

define LIBRETRO_YABASANSHIRO_BUILD_CMDS
	$(TARGET_CONFIGURE_OPTS) LDFLAGS="$(LIBRETRO_YABASANSHIRO_TARGET_LDFLAGS)" CFLAGS="$(LIBRETRO_YABASANSHIRO_TARGET_CFLAGS)" CXXFLAGS="$(LIBRETRO_YABASANSHIRO_TARGET_CFLAGS)" $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" \
		-C $(@D)/yabause/src/libretro -f Makefile platform="$(LIBRETRO_YABASANSHIRO_PLATFORM)" $(LIBRETRO_YABASANSHIRO_EXTRA_ARGS) \
        GIT_VERSION="-$(shell echo $(LIBRETRO_YABASANSHIRO_VERSION) | cut -c 1-7)"
endef

define LIBRETRO_YABASANSHIRO_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/yabause/src/libretro/yabasanshiro_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/yabasanshiro_libretro.so
endef

$(eval $(generic-package))
