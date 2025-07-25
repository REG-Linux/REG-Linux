################################################################################
#
# libretro-bsnes-jg
#
################################################################################
# Version: Commits on Jul 14, 2025
LIBRETRO_BSNES_JG_VERSION = 6400024854702110c4019f5b0a7336dca7112fdb
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
