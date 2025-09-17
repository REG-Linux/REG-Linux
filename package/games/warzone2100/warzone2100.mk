################################################################################
#
# Warzone 2100
#
################################################################################
# Version.: Release 4.6.1 on Sep 16, 2025
WARZONE2100_VERSION = 4.6.1
WARZONE2100_SOURCE = warzone2100_src.tar.xz
WARZONE2100_SITE = https://github.com/Warzone2100/warzone2100/releases/download/$(WARZONE2100_VERSION)

WARZONE2100_DEPENDENCIES =  sdl2 libsodium sqlite protobuf
WARZONE2100_DEPENDENCIES += libzip physfs openal libtheora libcurl

WARZONE2100_LICENSE = GPL-2.0

WARZONE2100_SUPPORTS_IN_SOURCE_BUILD = NO

WARZONE2100_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release

$(eval $(cmake-package))
