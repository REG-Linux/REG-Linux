################################################################################
#
# ares
#
################################################################################
# Version.: Release on Aug 27, 2025
ARES_VERSION = v146
ARES_SITE = $(call github,ares-emulator,ares,$(ARES_VERSION))
ARES_LICENSE = GPLv3
ARES_DEPENDENCIES = sdl2 libgl zlib pango cairo libgtk3 librashader xwayland
# This is needed for sourcery tool (cross-compiling)
ARES_DEPENDENCIES += host-ares

ARES_SUPPORTS_IN_SOURCE_BUILD = NO

ARES_CONF_OPTS  = -DCMAKE_BUILD_TYPE=Release
ARES_CONF_OPTS += -DBUILD_SHARED_LIBS=FALSE
ARES_CONF_OPTS += -DWITH_SYSTEM_ZLIB=ON
ARES_CONF_OPTS += -DARES_BUILD_LOCAL=OFF
ARES_CONF_OPTS += -DARES_ENABLE_MINIMUM_CPU=OFF

$(eval $(cmake-package))

HOST_ARES_CONF_OPTS  = -DCMAKE_BUILD_TYPE=Release
HOST_ARES_CONF_OPTS += -DBUILD_SHARED_LIBS=FALSE
HOST_ARES_CONF_OPTS += -DWITH_SYSTEM_ZLIB=ON
HOST_ARES_CONF_OPTS += -DARES_BUILD_LOCAL=OFF
HOST_ARES_CONF_OPTS += -DARES_ENABLE_MINIMUM_CPU=OFF
HOST_ARES_CONF_OPTS += -DARES_BUILD_SOURCERY_ONLY=ON
HOST_ARES_DEPENDENCIES = host-zlib
$(eval $(host-cmake-package))
