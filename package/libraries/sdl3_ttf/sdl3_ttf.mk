################################################################################
#
# sdl3_ttf
#
################################################################################

SDL3_TTF_VERSION = release-3.2.0
SDL3_TTF_SITE = https://github.com/libsdl-org/SDL_ttf.git
SDL3_TTF_SITE_METHOD = git
SDL3_TTF_GIT_SUBMODULES = yes
SDL3_TTF_LICENSE = Zlib
SDL3_TTF_LICENSE_FILES = LICENSE.txt
SDL3_TTF_INSTALL_STAGING = YES

ifeq ($(BR2_ENABLE_DEBUG),y)
SDL3_TTF_CONF_OPTS = -DCMAKE_BUILD_TYPE=Debug
else
SDL3_TTF_CONF_OPTS = -DCMAKE_BUILD_TYPE=Release
endif

SDL3_TTF_DEPENDENCIES += sdl3

ifeq ($(BR2_PACKAGE_FREETYPE),y)
SDL3_TTF_DEPENDENCIES += freetype
endif

ifeq ($(BR2_PACKAGE_HARFBUZZ),y)
SDL3_TTF_DEPENDENCIES += harfbuzz
endif

ifeq ($(BR2_PACKAGE_PLUTOSVG),y)
SDL3_TTF_DEPENDENCIES += plutosvg
endif

$(eval $(cmake-package))

# Host build specific option
#HOST_SDL3_TTF_CONF_OPTS += -DSDL_UNIX_CONSOLE_BUILD=ON
$(eval $(host-cmake-package))
