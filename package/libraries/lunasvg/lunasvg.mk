################################################################################
#
# lunasvg
#
################################################################################
# v3.2.1 is not properly aligned with plutovg
# LUNASVG_VERSION = v3.2.1
LUNASVG_VERSION = 84c71c543dde471e349a0fc33d9610a5e0a4eaf0
LUNASVG_SITE = $(call github,sammycage,lunasvg,$(LUNASVG_VERSION))
LUNASVG_LICENSE = MIT

LUNASVG_SUPPORTS_IN_SOURCE_BUILD = NO
LUNASVG_INSTALL_STAGING = YES

LUNASVG_DEPENDENCIES = plutovg

LUNASVG_CONF_OPTS  = -DCMAKE_BUILD_TYPE=Release
LUNASVG_CONF_OPTS += -DBUILD_SHARED_LIBS=TRUE

LUNASVG_CONF_ENV += LDFLAGS=-lpthread

$(eval $(cmake-package))
