################################################################################
#
# easyrpg-player
#
################################################################################
# Version: 0.8.1
EASYRPG_PLAYER_VERSION = 0.8.1
EASYRPG_PLAYER_LICENSE = MIT
EASYRPG_PLAYER_SITE = $(call github,EasyRPG,Player,$(EASYRPG_PLAYER_VERSION))
EASYRPG_PLAYER_SUPPORTS_IN_SOURCE_BUILD = NO

EASYRPG_PLAYER_DEPENDENCIES += sdl2 zlib fmt libpng freetype mpg123 libvorbis
EASYRPG_PLAYER_DEPENDENCIES += opusfile liblcf pixman speexdsp libxmp wildmidi
EASYRPG_PLAYER_DEPENDENCIES += json-for-modern-cpp libsndfile lhasa

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
