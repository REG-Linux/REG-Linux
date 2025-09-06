################################################################################
#
# sdl3_mixer
#
################################################################################

# Transitional branch sdl2-api-on-sdl3
SDL3_MIXER_VERSION = cbe70fa4d0fe307e266ae4d1a4a7d0dd7ea9e96c
SDL3_MIXER_SITE = https://github.com/libsdl-org/SDL_mixer.git
SDL3_MIXER_SITE_METHOD = git
SDL3_MIXER_GIT_SUBMODULES = yes
SDL3_MIXER_LICENSE = Zlib
SDL3_MIXER_LICENSE_FILES = LICENSE.txt
SDL3_MIXER_INSTALL_STAGING = YES

ifeq ($(BR2_ENABLE_DEBUG),y)
SDL3_MIXER_CONF_OPTS = -DCMAKE_BUILD_TYPE=Debug
else
SDL3_MIXER_CONF_OPTS = -DCMAKE_BUILD_TYPE=Release
endif

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

# Codecs
ifeq ($(BR2_PACKAGE_LIBOGG),y)
SDL3_MIXER_DEPENDENCIES += libogg
endif
ifeq ($(BR2_PACKAGE_LIBVORBIS),y)
SDL3_MIXER_DEPENDENCIES += libvorbis
endif
ifeq ($(BR2_PACKAGE_OPUS),y)
SDL3_MIXER_DEPENDENCIES += opus
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
