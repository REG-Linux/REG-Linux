################################################################################
#
# alephone — Aleph One (Marathon engine, Bungie's FPS trilogy)
#
################################################################################

ALEPHONE_VERSION = release-20260930
ALEPHONE_SITE = https://github.com/Aleph-One-Marathon/alephone
ALEPHONE_SITE_METHOD = git
ALEPHONE_LICENSE = GPL-3.0
ALEPHONE_LICENSE_FILES = COPYING

ALEPHONE_AUTORECONF = YES
ALEPHONE_DEPENDENCIES = sdl2 sdl2_ttf sdl2_image openal boost \
	zlib libsndfile libvorbis libogg libpng libcurl

ALEPHONE_CONF_OPTS = \
	--disable-opengl \
	--without-miniupnpc \
	--without-nfd \
	--without-catch2 \
	--without-zzip

ifeq ($(BR2_PACKAGE_HAS_LIBGL),y)
ALEPHONE_DEPENDENCIES += libgl libglu
ALEPHONE_CONF_OPTS = \
	--without-miniupnpc \
	--without-nfd \
	--without-catch2 \
	--without-zzip
endif

ifeq ($(BR2_PACKAGE_ZZIPLIB),y)
ALEPHONE_DEPENDENCIES += zziplib
ALEPHONE_CONF_OPTS += --with-zzip
endif

$(eval $(autotools-package))
