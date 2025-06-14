################################################################################
#
# libretro-beetle-saturn
#
################################################################################
# Version: Commits on Jun 14, 2025
LIBRETRO_BEETLE_SATURN_VERSION = a4dbc878928e1a2f7857f64ee2af782078fc150c
LIBRETRO_BEETLE_SATURN_SITE = $(call github,REG-Linux,beetle-saturn-libretro,$(LIBRETRO_BEETLE_SATURN_VERSION))
LIBRETRO_BEETLE_SATURN_LICENSE = GPLv2

LIBRETRO_BEETLE_SATURN_PLATFORM = $(LIBRETRO_PLATFORM)

ifeq ($(BR2_PACKAGE_HAS_LIBGLES),y)
LIBRETRO_BEETLE_SATURN_DEPENDENCIES += libgles
endif

ifeq ($(BR2_PACKAGE_HAS_LIBGL),y)
LIBRETRO_BEETLE_SATURN_DEPENDENCIES += libgl
else
LIBRETRO_BEETLE_SATURN_PLATFORM = $(LIBRETRO_PLATFORM)-gles
endif

define LIBRETRO_BEETLE_SATURN_BUILD_CMDS
	$(TARGET_CONFIGURE_OPTS) $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" \
	    -C $(@D) -f Makefile HAVE_OPENGL=1 platform="$(LIBRETRO_BEETLE_SATURN_PLATFORM)"
endef

define LIBRETRO_BEETLE_SATURN_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/mednafen_saturn_hw_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/beetle-saturn_libretro.so
endef

$(eval $(generic-package))
