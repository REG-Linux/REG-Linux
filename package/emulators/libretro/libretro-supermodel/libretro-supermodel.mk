################################################################################
#
# libretro-supermodel
#
################################################################################
# Version: Commits on Aug 23, 2026
LIBRETRO_SUPERMODEL_VERSION = 9f0a51daf6cef6ec2a304538f18c6dbb4c4b9da2
LIBRETRO_SUPERMODEL_SITE = $(call github,libretro,Libretro-Supermodel,$(LIBRETRO_SUPERMODEL_VERSION))
LIBRETRO_SUPERMODEL_LICENSE = GPLv3

LIBRETRO_SUPERMODEL_PLATFORM = $(LIBRETRO_PLATFORM)
LIBRETRO_SUPERMODEL_DEPENDENCIES += zlib
LIBRETRO_SUPERMODEL_TARGET_LDFLAGS = $(TARGET_LDFLAGS)

# REG: Right now, let's enforce GLES3 everywhere
# Desktop GL path (with Legacy3D) only with GL+XWayland
#ifeq ($(BR2_PACKAGE_HAS_LIBGL)$(BR2_PACKAGE_REGLINUX_XWAYLAND),yy)
#LIBRETRO_SUPERMODEL_DEPENDENCIES += libgl libglu
#LIBRETRO_SUPERMODEL_PLATFORM = unix
# Use GLES3/New3D renderer on ARM platforms (no GLU needed),
#else
ifeq ($(BR2_PACKAGE_HAS_LIBGLES),y)
LIBRETRO_SUPERMODEL_DEPENDENCIES += libgles
# What a ugly hack
LIBRETRO_SUPERMODEL_PLATFORM = aarch64
endif

define LIBRETRO_SUPERMODEL_BUILD_CMDS
	$(TARGET_CONFIGURE_OPTS) \
	    LDFLAGS="$(LIBRETRO_SUPERMODEL_TARGET_LDFLAGS)" \
	    $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" \
	    LD="$(TARGET_CXX)" -C $(@D) -f Makefile \
	    platform="$(LIBRETRO_SUPERMODEL_PLATFORM)" \
	    GIT_VERSION="-$(shell echo $(LIBRETRO_SUPERMODEL_VERSION) | cut -c 1-7)"
endef

define LIBRETRO_SUPERMODEL_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/supermodel_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/supermodel_libretro.so
	$(INSTALL) -D $(@D)/supermodel_libretro.info \
		$(TARGET_DIR)/usr/share/libretro/info/supermodel_libretro.info
endef

$(eval $(generic-package))
