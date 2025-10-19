################################################################################
#
# libmt32emu
#
################################################################################
CXXOPTS_VERSION = v3.3.1
CXXOPTS_SITE = $(call github,jarro2783,cxxopts,$(CXXOPTS_VERSION))
CXXOPTS_LICENSE = GPLv2

CXXOPTS_SUPPORTS_IN_SOURCE_BUILD = NO
CXXOPTS_INSTALL_STAGING = YES

CXXOPTS_CONF_OPTS  = -DCMAKE_BUILD_TYPE=Release
CXXOPTS_CONF_OPTS += -DBUILD_STATIC_LIBS=TRUE
CXXOPTS_CONF_OPTS += -DBUILD_SHARED_LIBS=FALSE

CXXOPTS_CONF_ENV += LDFLAGS=-lpthread

$(eval $(cmake-package))
