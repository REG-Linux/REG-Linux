################################################################################
#
# LIBGME
#
################################################################################

LIBGME_VERSION = 0.6.5
LIBGME_SITE = https://github.com/libgme/game-music-emu/releases/download/$(LIBGME_VERSION)
LIBGME_SOURCE = libgme-$(LIBGME_VERSION)-src.tar.gz
LIBGME_INSTALL_STAGING = YES
LIBGME_LICENSE = LGPL-2.1+
LIBGME_LICENSE_FILES = license.txt
LIBGME_DEPENDENCIES = host-pkgconf zlib

# Shared only; static unused, doubles install size.
# YM2612 emulator: Nuked (best quality, LGPL-2.1+) — keeps overall license LGPL.
# MAME variant is GPL-2+ and would taint the shared lib.
LIBGME_CONF_OPTS = \
	-DGME_BUILD_SHARED=ON \
	-DGME_BUILD_STATIC=OFF \
	-DGME_BUILD_TESTING=OFF \
	-DGME_BUILD_EXAMPLES=OFF \
	-DGME_ENABLE_UBSAN=OFF \
	-DGME_ENABLE_ASAN=OFF \
	-DGME_ZLIB=ON \
	-DGME_YM2612_EMU=Nuked \
	-DUSE_GME_AY=ON \
	-DUSE_GME_GBS=ON \
	-DUSE_GME_GYM=ON \
	-DUSE_GME_HES=ON \
	-DUSE_GME_KSS=ON \
	-DUSE_GME_NSF=ON \
	-DUSE_GME_NSFE=ON \
	-DUSE_GME_SAP=ON \
	-DUSE_GME_SPC=ON \
	-DUSE_GME_VGM=ON \
	-DGME_SPC_ISOLATED_ECHO_BUFFER=OFF

$(eval $(cmake-package))
