################################################################################
#
# devilutionx
#
################################################################################

# Version: Release 1.5.5 - Oct 30, 2025
DEVILUTIONX_VERSION = 1.5.5
DEVILUTIONX_SITE = https://github.com/diasurgical/devilutionX/releases/download/$(DEVILUTIONX_VERSION)
DEVILUTIONX_SOURCE = devilutionx-src.tar.xz
DEVILUTIONX_DEPENDENCIES = sdl2 sdl2_image fmt libsodium libpng bzip2
DEVILUTIONX_SUPPORTS_IN_SOURCE_BUILD = NO

DEVILUTIONX_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release
DEVILUTIONX_CONF_OPTS += -DBUILD_SHARED_LIBS=OFF
DEVILUTIONX_CONF_OPTS += -DBUILD_STATIC_LIBS=ON
# Prefill the player name when creating a new character, in case the device does
# not have a keyboard.
DEVILUTIONX_CONF_OPTS += -DBUILD_TESTING=OFF -DPREFILL_PLAYER_NAME=ON

# Ensure that DevilutionX's vendored dependencies are not accidentally fetched from network.
# They should all be present in the source package.
DEVILUTIONX_CONF_OPTS += -DFETCHCONTENT_FULLY_DISCONNECTED=ON

$(eval $(cmake-package))
