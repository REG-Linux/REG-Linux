################################################################################
#
# luanti — Voxel sandbox game engine (formerly Minetest)
#
################################################################################

LUANTI_VERSION = 5.17.0
LUANTI_SITE = https://github.com/minetest/minetest
LUANTI_SITE_METHOD = git
LUANTI_GIT_SUBMODULES = YES
LUANTI_LICENSE = LGPL-2.1+
LUANTI_LICENSE_FILES = LICENSE.txt

LUANTI_DEPENDENCIES = zlib zstd sqlite openssl gmp jsoncpp sdl2 \
	reglinux-luajit freetype openal libvorbis libogg libcurl libpng jpeg

LUANTI_SUPPORTS_IN_SOURCE_BUILD = NO
LUANTI_CONF_OPTS = \
	-DSDL2_DIR="$(STAGING_DIR)/usr/lib/cmake/SDL2" \
	-DBUILD_CLIENT=ON \
	-DBUILD_SERVER=OFF \
	-DBUILD_UNITTESTS=OFF \
	-DBUILD_BENCHMARKS=OFF \
	-DENABLE_GETTEXT=OFF \
	-DENABLE_CURSES=OFF \
	-DENABLE_LEVELDB=OFF \
	-DENABLE_REDIS=OFF \
	-DENABLE_POSTGRESQL=OFF \
	-DENABLE_SPATIAL=OFF \
	-DENABLE_PROMETHEUS=OFF \
	-DENABLE_LUAJIT=ON \
	-DRUN_IN_PLACE=OFF

ifeq ($(BR2_PACKAGE_HAS_LIBGLES),y)
LUANTI_DEPENDENCIES += libgles
LUANTI_CONF_OPTS += -DENABLE_OPENGL=OFF
LUANTI_CONF_OPTS += -DENABLE_GLES=ON
LUANTI_CONF_OPTS += -DENABLE_GLES2=ON
endif

ifeq ($(BR2_PACKAGE_HAS_LIBGL),y)
LUANTI_DEPENDENCIES += libgl
endif

$(eval $(cmake-package))
