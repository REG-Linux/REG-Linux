################################################################################
#
# easyrpg-player
#
################################################################################
# Version: v0.8 with fmt 10 fixes
EASYRPG_PLAYER_VERSION = a4672d2e30db4e4918c8f3580236faed3c9d04c1
EASYRPG_PLAYER_LICENSE = MIT
EASYRPG_PLAYER_SITE = $(call github,EasyRPG,Player,$(EASYRPG_PLAYER_VERSION))
EASYRPG_PLAYER_SUPPORTS_IN_SOURCE_BUILD = NO

EASYRPG_PLAYER_DEPENDENCIES += sdl2 zlib fmt libpng freetype mpg123 libvorbis
EASYRPG_PLAYER_DEPENDENCIES += opusfile liblcf pixman speexdsp libxmp wildmidi

ifeq ($(BR2_PACKAGE_HARFBUZZ),y)
EASYRPG_PLAYER_DEPENDENCIES += harfbuzz
endif

ifeq ($(BR2_PACKAGE_FLUIDSYNTH),y)
EASYRPG_PLAYER_DEPENDENCIES += fluidsynth
endif

EASYRPG_PLAYER_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release
EASYRPG_PLAYER_CONF_OPTS += -DPLAYER_BUILD_EXECUTABLE=ON
EASYRPG_PLAYER_CONF_OPTS += -DBUILD_SHARED_LIBS=ON
EASYRPG_PLAYER_CONF_OPTS += -DBUILD_STATIC_LIBS=ON

EASYRPG_PLAYER_CONF_ENV += LDFLAGS="-lpthread -fPIC" CFLAGS="-fPIC" CXX_FLAGS="-fPIC"

define EASYRPG_PLAYER_EVMAPY
	mkdir -p $(TARGET_DIR)/usr/share/evmapy
	cp $(BR2_EXTERNAL_REGLINUX_PATH)/package/engines/easyrpg/easyrpg-player/easyrpg.easyrpg.keys \
	    $(TARGET_DIR)/usr/share/evmapy
endef

EASYRPG_PLAYER_POST_INSTALL_TARGET_HOOKS += EASYRPG_PLAYER_EVMAPY

$(eval $(cmake-package))
