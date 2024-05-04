################################################################################
#
# MEDNAFEN
#
################################################################################
# Version.: Release on Apr 6, 2024
MEDNAFEN_VERSION = 1.32.1
MEDNAFEN_SOURCE = mednafen-$(MEDNAFEN_VERSION).tar.xz
MEDNAFEN_SITE = https://mednafen.github.io/releases/files
MEDNAFEN_LICENSE = GPLv3
MEDNAFEN_DEPENDENCIES = sdl2 zlib libpng flac

MEDNAFEN_CONF_OPTS = --disable-ssfplay

$(eval $(autotools-package))
