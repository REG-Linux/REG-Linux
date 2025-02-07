###############################################################################
#
# BLASTEM
#
################################################################################
# Version.: Commits on Feb 3, 2025
LIBRETRO_BLASTEM_VERSION = c9bfed9156dc
LIBRETRO_BLASTEM_SOURCE = $(LIBRETRO_BLASTEM_VERSION).tar.gz
LIBRETRO_BLASTEM_SITE = https://www.retrodev.com/repos/blastem/archive
LIBRETRO_BLASTEM_LICENSE = Non-commercial

define LIBRETRO_BLASTEM_BUILD_CMDS
	$(SED) "s+CPU:=i686+CPU?=i686+g" $(@D)/Makefile
	cd $(@D) && ./cpu_dsl.py z80.cpu > z80.c
	cd $(@D) && ./cpu_dsl.py m68k.cpu > m68k.c
	$(TARGET_CONFIGURE_OPTS) $(MAKE) CFLAGS="-Wno-error=incompatible-pointer-types -DHAS_PROC -DHAVE_UNISTD_H -fPIC -DNEW_CORE -DIS_LIB -std=gnu99" CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C $(@D) $(LIBRETRO_BLASTEM_EXTRAOPTS) libblastem.so
endef

define LIBRETRO_BLASTEM_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/libblastem.so \
		$(TARGET_DIR)/usr/lib/libretro/blastem_libretro.so
endef

$(eval $(generic-package))
