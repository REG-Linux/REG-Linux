################################################################################
#
# libretro-bsnes-jg
#
################################################################################
# Version: Commits on Sep 3, 2026
LIBRETRO_BSNES_JG_VERSION = aa11568fff267fca3424cbdfa6da788ddc42e468
LIBRETRO_BSNES_JG_SITE = $(call github,libretro,bsnes-jg,$(LIBRETRO_BSNES_JG_VERSION))
LIBRETRO_BSNES_JG_LICENSE = GPLv3
LIBRETRO_BSNES_JG_LICENSE_FILE = LICENSE.txt

define LIBRETRO_BSNES_JG_BUILD_CMDS
	$(TARGET_CONFIGURE_OPTS) $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C $(@D)/libretro \
	    -f Makefile platform="unix"
endef

define LIBRETRO_BSNES_JG_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/libretro/bsnes-jg_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/bsnes-jg_libretro.so
endef

$(eval $(generic-package))
