################################################################################
#
# lunasvg
#
################################################################################
LUNASVG_VERSION = v2.4.1
LUNASVG_SITE = https://github.com/sammycage/lunasvg
LUNASVG_SITE_METHOD = git
LUNASVG_LICENSE = MIT

LUNASVG_SUPPORTS_IN_SOURCE_BUILD = NO
LUNASVG_INSTALL_STAGING = YES

LUNASVG_CONF_OPTS  = -DCMAKE_BUILD_TYPE=Release
LUNASVG_CONF_OPTS += -DBUILD_SHARED_LIBS=TRUE

LUNASVG_CONF_ENV += LDFLAGS=-lpthread

$(eval $(cmake-package))
