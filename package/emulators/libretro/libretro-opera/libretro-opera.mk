################################################################################
#
# libretro-opera
#
################################################################################
# Version: Commits on Jun 17, 2025
LIBRETRO_OPERA_VERSION = e8f26aafd5a3f21fd3de0b3116f72cc5aeda8fbe
LIBRETRO_OPERA_SITE = $(call github,REG-Linux,opera-libretro,$(LIBRETRO_OPERA_VERSION))
LIBRETRO_OPERA_LICENSE = LGPL/Non-commercial

LIBRETRO_OPERA_PLATFORM=$(LIBRETRO_PLATFORM)

ifeq ($(BR2_PACKAGE_SYSTEM_TARGET_XU4),y)
LIBRETRO_OPERA_PLATFORM=unix-odroidxu

else ifeq ($(BR2_PACKAGE_SYSTEM_TARGET_S922X),y)
LIBRETRO_OPERA_PLATFORM=unix-CortexA73_G12B
endif

define LIBRETRO_OPERA_BUILD_CMDS
	$(TARGET_CONFIGURE_OPTS) $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C $(@D)/ \
	    platform="$(LIBRETRO_OPERA_PLATFORM)" \
	    GIT_VERSION="-$(shell echo $(LIBRETRO_OPERA_VERSION) | cut -c 1-7)"
endef

define LIBRETRO_OPERA_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/opera_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/opera_libretro.so
endef

$(eval $(generic-package))
