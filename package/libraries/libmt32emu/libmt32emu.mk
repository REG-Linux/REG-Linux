################################################################################
#
# libmt32emu
#
################################################################################
LIBMT32EMU_VERSION = libmt32emu_2_7_2
LIBMT32EMU_SITE = $(call github,munt,munt,$(LIBMT32EMU_VERSION))
LIBMT32EMU_LICENSE = GPLv2

LIBMT32EMU_SUPPORTS_IN_SOURCE_BUILD = NO
LIBMT32EMU_INSTALL_STAGING = YES

LIBMT32EMU_CONF_OPTS  = -DCMAKE_BUILD_TYPE=Release
LIBMT32EMU_CONF_OPTS += -DBUILD_STATIC_LIBS=FALSE
LIBMT32EMU_CONF_OPTS += -DBUILD_SHARED_LIBS=TRUE

LIBMT32EMU_SUBDIR = mt32emu

LIBMT32EMU_CONF_ENV += LDFLAGS=-lpthread

$(eval $(cmake-package))
