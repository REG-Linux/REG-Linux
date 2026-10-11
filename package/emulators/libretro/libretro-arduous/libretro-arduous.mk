################################################################################
#
# libretro-arduous
#
################################################################################
# Version: Commits on Apr 20, 2026
LIBRETRO_ARDUOUS_VERSION = 798e3950f1de7c69455bc988d55eafeebac5a1eb
LIBRETRO_ARDUOUS_SITE = https://github.com/libretro/arduous.git
LIBRETRO_ARDUOUS_SITE_METHOD=git
LIBRETRO_ARDUOUS_GIT_SUBMODULES=YES
LIBRETRO_ARDUOUS_LICENSE = GPLv2

define LIBRETRO_ARDUOUS_INSTALL_TARGET_CMDS
    $(INSTALL) -D $(@D)/arduous_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/arduous_libretro.so
endef

$(eval $(cmake-package))
