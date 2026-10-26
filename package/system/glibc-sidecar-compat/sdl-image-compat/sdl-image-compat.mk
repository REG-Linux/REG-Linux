################################################################################
#
# sdl-image-compat
#
# SDL_image 1.2 (libSDL_image-1.2.so.0) for the glibc sidecar, on sdl12-compat.
# Buildroot's sdl_image needs its SDL 1.2.15; same source and options.
#
################################################################################

SDL_IMAGE_COMPAT_VERSION = 5d792dde2f764daf15dc48521774a3354330db69
SDL_IMAGE_COMPAT_SITE = $(call github,libsdl-org,SDL_image,$(SDL_IMAGE_COMPAT_VERSION))
SDL_IMAGE_COMPAT_SOURCE = sdl_image-$(SDL_IMAGE_COMPAT_VERSION).tar.gz
SDL_IMAGE_COMPAT_DL_SUBDIR = sdl_image
SDL_IMAGE_COMPAT_LICENSE = Zlib
SDL_IMAGE_COMPAT_LICENSE_FILES = COPYING
SDL_IMAGE_COMPAT_INSTALL_STAGING = YES
SDL_IMAGE_COMPAT_DEPENDENCIES = sdl12-compat jpeg libpng webp

# Linked, not loaded at run time by soname
SDL_IMAGE_COMPAT_CONF_OPTS = \
	--with-sdl-prefix=$(STAGING_DIR)/usr \
	--with-sdl-exec-prefix=$(STAGING_DIR)/usr \
	--disable-sdltest \
	--disable-static \
	--disable-jpg-shared \
	--disable-png-shared \
	--disable-tif-shared \
	--disable-webp-shared \
	--enable-bmp --enable-gif --enable-jpg --enable-lbm --enable-pcx \
	--enable-png --enable-pnm --enable-tga --enable-webp --enable-xcf \
	--enable-xpm --enable-xv \
	--disable-tif

$(eval $(autotools-package))
