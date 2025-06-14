################################################################################
#
# libretro-beetle-psx
#
################################################################################
# Version: Commits on Jun 14, 2025
LIBRETRO_BEETLE_PSX_VERSION = b8dd9de6dba5fa0359c0a7df7f0b61a7fc503093
LIBRETRO_BEETLE_PSX_SITE = $(call github,REG-Linux,beetle-psx-libretro,$(LIBRETRO_BEETLE_PSX_VERSION))
LIBRETRO_BEETLE_PSX_LICENSE = GPLv2

# Platforms
LIBRETRO_BEETLE_PSX_PLATFORM = $(LIBRETRO_PLATFORM)
ifeq ($(BR2_PACKAGE_SYSTEM_TARGET_BCM2711),y)
LIBRETRO_BEETLE_PSX_PLATFORM = rpi4_64
else ifeq ($(BR2_PACKAGE_SYSTEM_TARGET_BCM2712),y)
LIBRETRO_BEETLE_PSX_PLATFORM = rpi5_64
endif

# OpenGL ES 2.0 vs 3.x
ifeq ($(BR2_PACKAGE_HAS_LIBGLES),y)
LIBRETRO_BEETLE_PSX_DEPENDENCIES += libgles
LIBRETRO_BEETLE_PSX_OUTFILE=mednafen_psx_libretro.so
ifeq ($(BR2_PACKAGE_HAS_GLES3),y)
LIBRETRO_BEETLE_PSX_EXTRAOPT += GLES3=1
else
LIBRETRO_BEETLE_PSX_EXTRAOPT += GLES=1
endif
endif

# Desktop GL (requires GL core 3.3+)
ifeq ($(BR2_PACKAGE_HAS_LIBGL),y)
LIBRETRO_BEETLE_PSX_DEPENDENCIES += libgl
LIBRETRO_BEETLE_PSX_EXTRAOPT += HAVE_OPENGL=1
LIBRETRO_BEETLE_PSX_OUTFILE=mednafen_psx_hw_libretro.so
endif

# Xwayland if built for desktop GL
ifeq ($(BR2_PACKAGE_XWAYLAND),y)
LIBRETRO_BEETLE_PSX_DEPENDENCIES += xwayland
endif

# Vulkan renderer (requires Vulkan 1.0+)
ifeq ($(BR2_PACKAGE_REGLINUX_VULKAN),y)
LIBRETRO_BEETLE_PSX_DEPENDENCIES += vulkan-headers vulkan-loader
LIBRETRO_BEETLE_PSX_EXTRAOPT += HAVE_VULKAN=1
LIBRETRO_BEETLE_PSX_OUTFILE=mednafen_psx_hw_libretro.so
endif

define LIBRETRO_BEETLE_PSX_BUILD_CMDS
    $(TARGET_CONFIGURE_OPTS) $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" \
        -C $(@D) -f Makefile $(LIBRETRO_BEETLE_PSX_EXTRAOPT) \
        platform="$(LIBRETRO_BEETLE_PSX_PLATFORM)" \
        GIT_VERSION="-$(shell echo $(LIBRETRO_BEETLE_PSX_VERSION) | cut -c 1-7)"
endef

define LIBRETRO_BEETLE_PSX_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/$(LIBRETRO_BEETLE_PSX_OUTFILE) \
		$(TARGET_DIR)/usr/lib/libretro/mednafen_psx_libretro.so
endef

$(eval $(generic-package))
