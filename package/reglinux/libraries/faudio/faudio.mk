################################################################################
#
# faudio
#
################################################################################

FAUDIO_VERSION = 25.03
FAUDIO_SITE = $(call github,FNA-XNA,FAudio,$(FAUDIO_VERSION))

FAUDIO_LICENSE = ZLIB
FAUDIO_LICENSE_FILES = LICENSE
FAUDIO_DEPENDENCIES = host-bison host-flex host-libtool sdl2
#disable gstreamer following BR bump 2024.11
#gstreamer1 gst1-plugins-base

# Should be set when the package cannot be built inside
# the source tree but needs a separate build directory.
FAUDIO_SUPPORTS_IN_SOURCE_BUILD = NO

# Install to staging to build wine with Faudio support
FAUDIO_INSTALL_STAGING = YES

FAUDIO_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release
#disable gstreamer following BR bump 2024.11
FAUDIO_CONF_OPTS += -DGSTREAMER=OFF
# Choose from SDL2 / SDL3
ifeq ($(BR2_PACKAGE_SDL3),y)
FAUDIO_CONF_OPTS += -DBUILD_SDL3=ON
else
FAUDIO_CONF_OPTS += -DBUILD_SDL3=OFF
FAUDIO_CONF_OPTS += -DSDL2_INCLUDE_DIRS=$(STAGING_DIR)/usr/include/SDL2
FAUDIO_CONF_OPTS += -DSDL2_LIBRARIES=$(STAGING_DIR)/usr/lib/libSDL2.so
endif

# Wine
ifeq ($(BR2_PACKAGE_WINE_GE_CUSTOM),y)
FAUDIO_DEPENDENCIES += host-wine-ge-custom
endif

$(eval $(cmake-package))
