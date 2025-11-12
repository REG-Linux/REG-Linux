################################################################################
#
# eduke32
#
################################################################################
# Version: Commits on Nov 11, 2025
EDUKE32_VERSION = 39967d86610a140c9d372788f0bc2bb1992bd35c
EDUKE32_SITE = https://voidpoint.io/terminx/eduke32/-/archive/$(EDUKE32_VERSION)
EDUKE32_DEPENDENCIES = sdl2 flac libvpx
EDUKE32_LICENSE = GPL-2.0

ifeq ($(BR2_TOOLCHAIN_USES_MUSL),y)
EDUKE32_DEPENDENCIES += libexecinfo
endif

# Some build options are documented here:
# https://wiki.eduke32.com/wiki/Building_EDuke32_on_Linux
EDUKE32_BUILD_ARGS = STARTUP_WINDOW=0
EDUKE32_BUILD_ARGS += HAVE_GTK2=0
EDUKE32_BUILD_ARGS += OPTOPT="-ffast-math"
EDUKE32_BUILD_ARGS += USE_OPENGL=1
EDUKE32_BUILD_ARGS += CFLAGS="$(TARGET_CFLAGS) -I$(STAGING_DIR)/usr/include/SDL2"
EDUKE32_BUILD_ARGS += CXXFLAGS="$(TARGET_CXXFLAGS) -I$(STAGING_DIR)/usr/include/SDL2"

ifeq ($(BR2_TOOLCHAIN_USES_MUSL),y)
EDUKE32_BUILD_ARGS += LDFLAGS="$(TARGET_LDFLAGS) -lexecinfo"
endif

# Select OpenGL or OpenGL ES
ifeq ($(BR2_PACKAGE_HAS_LIBGL),y)
    EDUKE32_DEPENDENCIES += libgl
else ifeq ($(BR2_PACKAGE_HAS_LIBGLES),y)
    EDUKE32_BUILD_ARGS += EDUKE32_GLES=1
    EDUKE32_DEPENDENCIES += libgles
endif

define EDUKE32_BUILD_CMDS
    $(MAKE) SYSROOT="$(STAGING_DIR)" STRIP="$(TARGET_STRIP)" CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" $(EDUKE32_BUILD_ARGS) -C $(@D)
    $(RM) -r $(@D)/obj
    $(MAKE) SYSROOT="$(STAGING_DIR)" STRIP="$(TARGET_STRIP)" CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" $(EDUKE32_BUILD_ARGS) FURY=1 -C $(@D)
endef

define EDUKE32_INSTALL_TARGET_CMDS
    $(INSTALL) -D -m 0755 $(@D)/eduke32 $(TARGET_DIR)/usr/bin/eduke32
    $(INSTALL) -D -m 0755 $(@D)/fury $(TARGET_DIR)/usr/bin/fury
    mkdir -p $(TARGET_DIR)/usr/share/evmapy
    cp $(BR2_EXTERNAL_REGLINUX_PATH)/package/ports/eduke32/eduke32.keys \
        $(TARGET_DIR)/usr/share/evmapy
    cp $(BR2_EXTERNAL_REGLINUX_PATH)/package/ports/eduke32/eduke32.keys \
        $(TARGET_DIR)/usr/share/evmapy/fury.keys
endef

$(eval $(generic-package))
