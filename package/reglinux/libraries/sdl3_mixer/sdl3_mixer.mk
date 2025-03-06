################################################################################
#
# sdl3_mixer
#
################################################################################

SDL3_MIXER_VERSION = 78a2035cf4cf95066d7d9e6208e99507376409a7
SDL3_MIXER_SITE = https://github.com/libsdl-org/SDL_mixer.git
SDL3_MIXER_SITE_METHOD = git
SDL3_MIXER_GIT_SUBMODULES = yes
SDL3_MIXER_LICENSE = Zlib
SDL3_MIXER_LICENSE_FILES = LICENSE.txt
SDL3_MIXER_INSTALL_STAGING = YES

SDL3_MIXER_DEPENDENCIES += sdl3

# FLAC
ifeq ($(BR2_PACKAGE_FLAC),y)
SDL3_MIXER_DEPENDENCIES += flac
endif

# MIDI
ifeq ($(BR2_PACKAGE_FLUIDSYNTH),y)
SDL3_MIXER_DEPENDENCIES += fluidsynth
endif

# Modules
ifeq ($(BR2_PACKAGE_LIBXMP),y)
SDL3_MIXER_DEPENDENCIES += libxmp
endif

# Backends
ifeq ($(BR2_PACKAGE_ALSA_LIB),y)
SDL3_MIXER_DEPENDENCIES += alsa-lib
endif
ifeq ($(BR2_PACKAGE_PIPEWIRE),y)
SDL3_MIXER_DEPENDENCIES += pipewire
endif

$(eval $(cmake-package))

# Host build specific option
#HOST_SDL3_MIXER_CONF_OPTS += -DSDL_UNIX_CONSOLE_BUILD=ON
$(eval $(host-cmake-package))
