################################################################################
#
# libretro-amiberry
#
################################################################################

LIBRETRO_AMIBERRY_VERSION = v8.3.0
LIBRETRO_AMIBERRY_SITE = https://github.com/BlitterStudio/amiberry
LIBRETRO_AMIBERRY_SITE_METHOD = git
LIBRETRO_AMIBERRY_GIT_SUBMODULES = YES
LIBRETRO_AMIBERRY_LICENSE = GPLv3
LIBRETRO_AMIBERRY_DEPENDENCIES = zlib json-for-modern-cpp

define LIBRETRO_AMIBERRY_BUILD_CMDS
	$(TARGET_CONFIGURE_OPTS) $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" \
		-C $(@D)/libretro -f Makefile platform="unix"
endef

define LIBRETRO_AMIBERRY_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/libretro/amiberry_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/amiberry_libretro.so
endef

$(eval $(generic-package))
