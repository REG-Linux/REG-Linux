################################################################################
#
# libretro-vecx
#
################################################################################
# Version.: Commits on Apr 11, 2026
LIBRETRO_VECX_VERSION = 8f671cc9d737f2890c3ce19e177e2984dcae121f
LIBRETRO_VECX_SITE = $(call github,libretro,libretro-vecx,$(LIBRETRO_VECX_VERSION))
LIBRETRO_VECX_LICENSE = GPLv2|LGPLv2.1

LIBRETRO_VECX_PLATFORM = $(LIBRETRO_PLATFORM)

# OpenGL backend — must match RetroArch's API selection.
# Key off HAS_DESKTOP_OPENGL rather than HAS_LIBGL (polluted by XWayland).
ifeq ($(BR2_PACKAGE_HAS_DESKTOP_OPENGL),y)
LIBRETRO_VECX_DEPENDENCIES += libgl
else ifeq ($(BR2_PACKAGE_HAS_LIBGLES),y)
LIBRETRO_VECX_DEPENDENCIES += libgles
LIBRETRO_VECX_MAKE_OPTS += GLES=1
LIBRETRO_VECX_MAKE_OPTS += GL_LIB=-lGLESv2
else
LIBRETRO_VECX_MAKE_OPTS += HAS_GPU=0
endif

ifeq ($(BR2_PACKAGE_SYSTEM_TARGET_RPI_ANY),y)
LIBRETRO_VECX_PLATFORM = rpi-mesa

else ifeq ($(BR2_aarch64),y)
LIBRETRO_VECX_PLATFORM = unix

else ifeq ($(BR2_PACKAGE_SYSTEM_TARGET_S812),y)
LIBRETRO_VECX_PLATFORM = armv
endif

define LIBRETRO_VECX_BUILD_CMDS
	$(TARGET_CONFIGURE_OPTS) $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C $(@D)/ -f Makefile.libretro  platform="$(LIBRETRO_VECX_PLATFORM)" $(LIBRETRO_VECX_MAKE_OPTS) \
        GIT_VERSION="-$(shell echo $(LIBRETRO_VECX_VERSION) | cut -c 1-7)"
endef

define LIBRETRO_VECX_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/vecx_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/vecx_libretro.so
endef

$(eval $(generic-package))
