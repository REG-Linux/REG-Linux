################################################################################
#
# MEDNAFEN
#
################################################################################
# Release on Apr 6, 2024
#MEDNAFEN_VERSION = 1.32.1
#MEDNAFEN_SOURCE = mednafen-$(MEDNAFEN_VERSION).tar.xz
#https://mednafen.github.io/releases/files
# REG fork with CHD support
MEDNAFEN_VERSION = b04f030165979292fcb817dd8cdc2a31b2bec2b6
MEDNAFEN_SITE = https://github.com/REG-Linux/mednafen.git
MEDNAFEN_SITE_METHOD = git
MEDNAFEN_LICENSE = GPLv3
MEDNAFEN_DEPENDENCIES = sdl2 zlib libpng flac

# Disable mednafen unused cores
MEDNAFEN_CONF_OPTS  = --disable-ssfplay --disable-sasplay
MEDNAFEN_CONF_OPTS += --disable-nes --disable-snes --disable-snes-faust
MEDNAFEN_CONF_OPTS += --disable-gb --disable-gba
MEDNAFEN_CONF_OPTS += --disable-sms --disable-md

# Disable mednafen unused features
MEDNAFEN_CONF_OPTS += --disable-debugger

# Configurable PCFX core
ifeq ($(BR2_PACKAGE_MEDNAFEN_PCFX),y)
MEDNAFEN_CONF_OPTS += --enable-pcfx
else
MEDNAFEN_CONF_OPTS += --disable-pcfx
endif

# Configurable PSX core
ifeq ($(BR2_PACKAGE_MEDNAFEN_PSX),y)
MEDNAFEN_CONF_OPTS += --enable-psx
else
MEDNAFEN_CONF_OPTS += --disable-psx
endif

# Configurable Saturn core
ifeq ($(BR2_PACKAGE_MEDNAFEN_SATURN),y)
MEDNAFEN_CONF_OPTS += --enable-ss
else
MEDNAFEN_CONF_OPTS += --disable-ss
endif

# Link mednafen with external libraries when possible
ifeq ($(BR2_PACKAGE_ZSTD),y)
MEDNAFEN_DEPENDENCIES += zstd
MEDNAFEN_CONF_OPTS += --with-external-libzstd
endif
ifeq ($(BR2_PACKAGE_LZO),y)
MEDNAFEN_DEPENDENCIES += lzo
MEDNAFEN_CONF_OPTS +=  --with-external-lzo
endif

$(eval $(autotools-package))
