################################################################################
#
# plutosvg
#
################################################################################
PLUTOSVG_VERSION = v0.0.6
PLUTOSVG_SITE = $(call github,sammycage,plutosvg,$(PLUTOSVG_VERSION))
PLUTOSVG_LICENSE = MIT

PLUTOSVG_SUPPORTS_IN_SOURCE_BUILD = NO
PLUTOSVG_INSTALL_STAGING = YES

PLUTOSVG_DEPENDENCIES = plutovg

PLUTOSVG_CONF_OPTS  = -DCMAKE_BUILD_TYPE=Release
PLUTOSVG_CONF_OPTS += -DBUILD_SHARED_LIBS=TRUE

PLUTOSVG_CONF_ENV += LDFLAGS=-lpthread

$(eval $(cmake-package))
