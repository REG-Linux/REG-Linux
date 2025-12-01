################################################################################
#
# OpenRCT2 (Roller Coaster Tycoon 2 open source engine)
#
################################################################################
# Version.: Release 0.4.26 on Sep 16, 2025
OPENRCT2_VERSION = v0.4.26
OPENRCT2_SITE = $(call github,OpenRCT2,OpenRCT2,$(OPENRCT2_VERSION))

OPENRCT2_DEPENDENCIES  = sdl2 libcurl libzip speexdsp flac libvorbis
OPENRCT2_DEPENDENCIES += json-for-modern-cpp

# We need host build to process data
#OPENRCT2_DEPENDENCIES += host-openrct2

# Out-of-tree build is enforced in CMake
OPENRCT2_SUPPORTS_IN_SOURCE_BUILD = NO

OPENRCT2_LICENSE = GPL-3.0

# No discord, enforce static building
OPENRCT2_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release
OPENRCT2_CONF_OPTS += -DBUILD_SHARED_LIBS=OFF
OPENRCT2_CONF_OPTS += -DBUILD_STATIC_LIBS=ON
OPENRCT2_CONF_OPTS += -DDISABLE_DISCORD_RPC=ON

# No OpenGL ES support ?
ifeq ($(BR2_PACKAGE_HAS_OPENGL),y)
OPENRCT2_CONF_OPTS += -DDISABLE_OPENGL=OFF
OPENRCT2_DEPENDENCIES += gl
else
OPENRCT2_CONF_OPTS += -DDISABLE_OPENGL=ON
endif

$(eval $(cmake-package))

#HOST_OPENRCT2_DEPENDENCIES = host-libzip host-libpng host-json-for-modern-cpp
#HOST_OPENRCT2_CONF_OPTS += -DDISABLE_GUI=ON
#HOST_OPENRCT2_CONF_OPTS += -DDISABLE_OPENGL=ON
#HOST_OPENRCT2_CONF_OPTS += -DDISABLE_DISCORD_RPC=ON
#HOST_OPENRCT2_CONF_OPTS += -DCMAKE_CXX_FLAGS="-Wno-error"
#$(eval $(host-cmake-package))
