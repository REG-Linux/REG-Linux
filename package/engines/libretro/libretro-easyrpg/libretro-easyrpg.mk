################################################################################
#
# libretro-easyrpg
#
################################################################################
# Version: 0.8.1.1
LIBRETRO_EASYRPG_VERSION = 0.8.1.1
LIBRETRO_EASYRPG_SITE = https://github.com/EasyRPG/Player
LIBRETRO_EASYRPG_GIT_SUBMODULES=YES
LIBRETRO_EASYRPG_SITE_METHOD=git
LIBRETRO_EASYRPG_LICENSE = GPLv3
LIBRETRO_EASYRPG_SUPPORTS_IN_SOURCE_BUILD = NO

LIBRETRO_EASYRPG_DEPENDENCIES = sdl2 zlib fmt libpng freetype mpg123 libvorbis
LIBRETRO_EASYRPG_DEPENDENCIES += opusfile pixman speexdsp libxmp wildmidi liblcf
LIBRETRO_EASYRPG_DEPENDENCIES += json-for-modern-cpp libsndfile lhasa

ifeq ($(BR2_PACKAGE_HARFBUZZ),y)
LIBRETRO_EASYRPG_DEPENDENCIES += harfbuzz
endif

ifeq ($(BR2_PACKAGE_FLUIDSYNTH),y)
LIBRETRO_EASYRPG_DEPENDENCIES += fluidsynth
endif

LIBRETRO_EASYRPG_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release
LIBRETRO_EASYRPG_CONF_OPTS += -DPLAYER_TARGET_PLATFORM=libretro
LIBRETRO_EASYRPG_CONF_OPTS += -DBUILD_SHARED_LIBS=ON
LIBRETRO_EASYRPG_CONF_OPTS += -DBUILD_STATIC_LIBS=ON
LIBRETRO_EASYRPG_CONF_ENV += LDFLAGS="-lpthread -fPIC" CFLAGS="-fPIC" CXX_FLAGS="-fPIC"

define LIBRETRO_EASYRPG_INSTALL_TARGET_CMDS
    $(INSTALL) -D $(@D)/buildroot-build/easyrpg_libretro.so \
    $(TARGET_DIR)/usr/lib/libretro/easyrpg_libretro.so
endef

$(eval $(cmake-package))
