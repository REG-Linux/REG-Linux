################################################################################
#
# faudio
#
################################################################################

FAUDIO_VERSION = 25.03
FAUDIO_SITE = $(call github,FNA-XNA,FAudio,$(FAUDIO_VERSION))
FAUDIO_LICENSE = ZLIB
FAUDIO_LICENSE_FILES = LICENSE
FAUDIO_SUPPORTS_IN_SOURCE_BUILD = NO
FAUDIO_DEPENDENCIES = host-bison host-flex host-libtool
FAUDIO_INSTALL_STAGING = YES

FAUDIO_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release

#disable gstreamer following BR bump 2024.11
FAUDIO_CONF_OPTS += -DGSTREAMER=OFF
#FAUDIO_DEPENDENCIES += gstreamer1 gst1-plugins-base

# SDL3 all the way
FAUDIO_DEPENDENCIES += sdl3
FAUDIO_CONF_OPTS += -DBUILD_SDL3=ON

# Wine
ifeq ($(BR2_PACKAGE_WINE_GE_CUSTOM),y)
FAUDIO_DEPENDENCIES += host-wine-ge-custom
endif

$(eval $(cmake-package))
