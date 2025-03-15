################################################################################
#
# sdl2_mixer
#
################################################################################

# reglinux - bump
SDL2_MIXER_VERSION = 2.8.1
SDL2_MIXER_SOURCE = SDL2_mixer-$(SDL2_MIXER_VERSION).tar.gz
SDL2_MIXER_SITE = http://www.libsdl.org/projects/SDL_mixer/release
SDL2_MIXER_LICENSE = Zlib
SDL2_MIXER_LICENSE_FILES = LICENSE.txt
SDL2_MIXER_INSTALL_STAGING = YES
SDL2_MIXER_DEPENDENCIES = sdl2 host-pkgconf

ifeq ($(BR2_PACKAGE_FLAC),y)
SDL2_MIXER_CONF_OPTS += --enable-music-flac
SDL2_MIXER_DEPENDENCIES += flac
else
SDL2_MIXER_CONF_OPTS += --disable-music-flac
endif

ifeq ($(BR2_PACKAGE_FLUIDSYNTH),y)
SDL2_MIXER_CONF_OPTS += --enable-music-midi-fluidsynth
SDL2_MIXER_DEPENDENCIES += fluidsynth
else
SDL2_MIXER_CONF_OPTS += --disable-music-midi-fluidsynth
endif

# REG enforce disabling libmodplug
SDL2_MIXER_CONF_OPTS += --disable-music-mod-modplug
# REG we use libxmp instead for modules playback
ifeq ($(BR2_PACKAGE_LIBXMP),y)
SDL2_MIXER_CONF_OPTS += --enable-music-mod-xmp
SDL2_MIXER_DEPENDENCIES += libxmp
else
SDL2_MIXER_CONF_OPTS += --disable-music-mod-xmp
endif

ifeq ($(BR2_PACKAGE_OPUSFILE),y)
SDL2_MIXER_CONF_OPTS += --enable-music-opus
SDL2_MIXER_DEPENDENCIES += opusfile
else
SDL2_MIXER_CONF_OPTS += --disable-music-opus
endif

ifeq ($(BR2_PACKAGE_TREMOR),y)
SDL2_MIXER_CONF_OPTS += --enable-music-ogg-tremor
SDL2_MIXER_DEPENDENCIES += tremor
else
SDL2_MIXER_CONF_OPTS += --disable-music-ogg-tremor
endif

# batocera
ifeq ($(BR2_PACKAGE_LIBMAD),y)
SDL2_MIXER_CONF_OPTS += --enable-music-mp3-mad-gpl
SDL2_MIXER_DEPENDENCIES += libmad
endif

# batocera
ifeq ($(BR2_PACKAGE_LIBVORBIS),y)
SDL2_MIXER_DEPENDENCIES += libvorbis
endif

$(eval $(autotools-package))
