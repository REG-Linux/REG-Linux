################################################################################
#
# sdl3-mixer
#
################################################################################

SDL3_MIXER_VERSION = 4be37aed1a4b76df71a814fbfa8ec9983f3b5508
SDL3_MIXER_SITE = https://github.com/libsdl-org/SDL_mixer.git
SDL3_MIXER_SITE_METHOD = git
SDL3_MIXER_GIT_SUBMODULES = yes
SDL3_MIXER_LICENSE = Zlib
SDL3_MIXER_LICENSE_FILES = LICENSE.txt
SDL3_MIXER_INSTALL_STAGING = YES

SDL3_MIXER_DEPENDENCIES += sdl3

ifeq ($(BR2_PACKAGE_PIPEWIRE),y)
SDL3_MIXER_DEPENDENCIES += pipewire
endif

ifeq ($(BR2_PACKAGE_ALSA_LIB),y)
SDL3_MIXER_DEPENDENCIES += alsa-lib
endif

$(eval $(cmake-package))

# Host build specific option
#HOST_SDL3_MIXER_CONF_OPTS += -DSDL_UNIX_CONSOLE_BUILD=ON
$(eval $(host-cmake-package))
