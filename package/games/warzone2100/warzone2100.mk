################################################################################
#
# Warzone 2100
#
################################################################################
# Version.: Release 4.7.0 on Apr 10, 2026
WARZONE2100_VERSION = 4.7.0
WARZONE2100_SOURCE = warzone2100_src.tar.xz
WARZONE2100_SITE = https://github.com/Warzone2100/warzone2100/releases/download/$(WARZONE2100_VERSION)

WARZONE2100_DEPENDENCIES =  sdl3 libsodium sqlite protobuf host-zip
WARZONE2100_DEPENDENCIES += libzip physfs openal libtheora libcurl

WARZONE2100_LICENSE = GPL-2.0

WARZONE2100_SUPPORTS_IN_SOURCE_BUILD = NO

WARZONE2100_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release

$(eval $(cmake-package))
