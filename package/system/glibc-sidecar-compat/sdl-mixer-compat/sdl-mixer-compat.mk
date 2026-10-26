################################################################################
#
# sdl-mixer-compat
#
# SDL_mixer 1.2 (libSDL_mixer-1.2.so.0) for the glibc sidecar, on
# sdl12-compat. Buildroot's sdl_mixer needs its SDL 1.2.15; same source,
# patches and options, with what the sidecar has: Ogg Vorbis, MOD through
# libmodplug, MIDI through fluidsynth.
#
################################################################################

SDL_MIXER_COMPAT_VERSION = d1725fcb7c4e987aeb7ecdc94cb8b6375b702170
SDL_MIXER_COMPAT_SITE = $(call github,libsdl-org,SDL_mixer,$(SDL_MIXER_COMPAT_VERSION))
SDL_MIXER_COMPAT_SOURCE = sdl_mixer-$(SDL_MIXER_COMPAT_VERSION).tar.gz
SDL_MIXER_COMPAT_DL_SUBDIR = sdl_mixer
SDL_MIXER_COMPAT_LICENSE = Zlib
SDL_MIXER_COMPAT_LICENSE_FILES = COPYING
SDL_MIXER_COMPAT_MAKE = $(MAKE1)
SDL_MIXER_COMPAT_INSTALL_STAGING = YES
SDL_MIXER_COMPAT_AUTORECONF = YES
SDL_MIXER_COMPAT_DEPENDENCIES = sdl12-compat host-pkgconf libvorbis libmodplug fluidsynth

# Linked, not loaded at run time by soname
SDL_MIXER_COMPAT_CONF_OPTS = \
	--with-sdl-prefix=$(STAGING_DIR)/usr \
	--disable-music-mod \
	--disable-music-mp3 \
	--disable-music-flac \
	--disable-music-mp3-mad-gpl \
	--enable-music-ogg \
	--disable-music-ogg-shared \
	--enable-music-mod-modplug \
	--disable-music-mod-modplug-shared \
	--enable-music-midi \
	--enable-music-fluidsynth-midi \
	--disable-music-fluidsynth-shared \
	--enable-music-timidity-midi

$(eval $(autotools-package))
