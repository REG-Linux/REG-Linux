################################################################################
#
# REG-Player
#
################################################################################

REGPLAYER_VERSION = v0.2.0
REGPLAYER_SITE = $(call github,REG-Linux,REG-Player,$(REGPLAYER_VERSION))
REGPLAYER_LICENSE = MIT
REGPLAYER_LICENSE_FILES = LICENSE
REGPLAYER_SUPPORTS_IN_SOURCE_BUILD = NO

REGPLAYER_DEPENDENCIES = \
	sdl3 sdl3_image sdl3_ttf \
	mpv taglib \
	libxmp libgme opusfile \
	alsa-lib zlib

# Bundled in source tree (no separate buildroot package):
#   - third_party/stsound  (LGPL, Atari ST .ym/.sndh)
#   - third_party/tinysid  (WTFPL, C64 .sid)
#   - third_party/miniaudio, stb, nlohmann/json (header-only)

REGPLAYER_CONF_OPTS = \
	-DCMAKE_BUILD_TYPE=Release \
	-DCMAKE_INSTALL_PREFIX=/usr

$(eval $(cmake-package))
