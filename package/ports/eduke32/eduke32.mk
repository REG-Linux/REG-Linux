################################################################################
#
# eduke32
#
################################################################################
# Version: Commits on Jul 13, 2025
EDUKE32_VERSION = 126f35ca8c24368f101996523935d08b269f45be
EDUKE32_SITE = https://voidpoint.io/terminx/eduke32/-/archive/$(EDUKE32_VERSION)
EDUKE32_DEPENDENCIES = sdl2 flac libvpx
EDUKE32_LICENSE = GPL-2.0

# Some build options are documented here:
# https://wiki.eduke32.com/wiki/Building_EDuke32_on_Linux
EDUKE32_BUILD_ARGS = STARTUP_WINDOW=0
EDUKE32_BUILD_ARGS += HAVE_GTK2=0
EDUKE32_BUILD_ARGS += OPTOPT="-ffast-math"
EDUKE32_BUILD_ARGS += USE_OPENGL=1
EDUKE32_BUILD_ARGS += CFLAGS="$(TARGET_CFLAGS) -I$(STAGING_DIR)/usr/include/SDL2"
EDUKE32_BUILD_ARGS += CXXFLAGS="$(TARGET_CXXFLAGS) -I$(STAGING_DIR)/usr/include/SDL2"

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
