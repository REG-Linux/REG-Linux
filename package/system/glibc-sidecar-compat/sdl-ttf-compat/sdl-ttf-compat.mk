################################################################################
#
# sdl-ttf-compat
#
# SDL_ttf 2.0 for SDL 1.2 (libSDL_ttf-2.0.so.0) for the glibc sidecar, on
# sdl12-compat. Buildroot's sdl_ttf needs its SDL 1.2.15; same source and
# options.
#
################################################################################

SDL_TTF_COMPAT_VERSION = 70b2940cc75e92aab02a67d2f827caf2836a2c74
SDL_TTF_COMPAT_SITE = $(call github,libsdl-org,SDL_ttf,$(SDL_TTF_COMPAT_VERSION))
SDL_TTF_COMPAT_SOURCE = sdl_ttf-$(SDL_TTF_COMPAT_VERSION).tar.gz
SDL_TTF_COMPAT_DL_SUBDIR = sdl_ttf
SDL_TTF_COMPAT_LICENSE = Zlib
SDL_TTF_COMPAT_LICENSE_FILES = COPYING
SDL_TTF_COMPAT_INSTALL_STAGING = YES
SDL_TTF_COMPAT_DEPENDENCIES = sdl12-compat freetype

SDL_TTF_COMPAT_CONF_OPTS = \
	--without-x \
	--with-freetype-prefix=$(STAGING_DIR)/usr \
	--with-sdl-prefix=$(STAGING_DIR)/usr
SDL_TTF_COMPAT_MAKE_OPTS = \
	INCLUDES="-I$(STAGING_DIR)/usr/include/SDL" \
	LDFLAGS="-L$(STAGING_DIR)/usr/lib"

$(eval $(autotools-package))
