################################################################################
#
# sdl3_image
#
################################################################################

SDL3_IMAGE_VERSION = release-3.2.6
SDL3_IMAGE_SITE = https://github.com/libsdl-org/SDL_image.git
SDL3_IMAGE_SITE_METHOD = git
SDL3_IMAGE_GIT_SUBMODULES = yes
SDL3_IMAGE_LICENSE = Zlib
SDL3_IMAGE_LICENSE_FILES = LICENSE.txt
SDL3_IMAGE_INSTALL_STAGING = YES

ifeq ($(BR2_ENABLE_DEBUG),y)
SDL3_IMAGE_CONF_OPTS = -DCMAKE_BUILD_TYPE=Debug
else
SDL3_IMAGE_CONF_OPTS = -DCMAKE_BUILD_TYPE=Release
endif

SDL3_IMAGE_DEPENDENCIES += sdl3 tiff webp #libavif

$(eval $(cmake-package))

# Host build specific option
#HOST_SDL3_IMAGE_CONF_OPTS += -DSDL_UNIX_CONSOLE_BUILD=ON
$(eval $(host-cmake-package))
