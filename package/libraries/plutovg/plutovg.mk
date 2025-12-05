################################################################################
#
# plutovg
#
################################################################################
PLUTOVG_VERSION = v1.3.2
PLUTOVG_SITE = $(call github,sammycage,plutovg,$(PLUTOVG_VERSION))
PLUTOVG_LICENSE = MIT

PLUTOVG_SUPPORTS_IN_SOURCE_BUILD = NO
PLUTOVG_INSTALL_STAGING = YES

PLUTOVG_CONF_OPTS  = -DCMAKE_BUILD_TYPE=Release
PLUTOVG_CONF_OPTS += -DBUILD_SHARED_LIBS=TRUE

PLUTOVG_CONF_ENV += LDFLAGS=-lpthread

$(eval $(cmake-package))
