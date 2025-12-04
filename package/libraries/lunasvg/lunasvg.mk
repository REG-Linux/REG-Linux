################################################################################
#
# lunasvg
#
################################################################################
LUNASVG_VERSION = v3.5.0
LUNASVG_SITE = $(call github,sammycage,lunasvg,$(LUNASVG_VERSION))
LUNASVG_LICENSE = MIT

LUNASVG_SUPPORTS_IN_SOURCE_BUILD = NO
LUNASVG_INSTALL_STAGING = YES

LUNASVG_DEPENDENCIES = plutovg

LUNASVG_CONF_OPTS  = -DCMAKE_BUILD_TYPE=Release
LUNASVG_CONF_OPTS += -DBUILD_SHARED_LIBS=TRUE

LUNASVG_CONF_ENV += LDFLAGS=-lpthread

$(eval $(cmake-package))
