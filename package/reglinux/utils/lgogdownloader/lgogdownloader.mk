################################################################################
#
# lgoddownloader
#
################################################################################
LGOGDOWNLOADER_VERSION = v3.14
LGOGDOWNLOADER_SITE = $(call github,Sude-,lgogdownloader,$(LGOGDOWNLOADER_VERSION))
LGOGDOWNLOADER_LICENSE = WTFPL
LGOGDOWNLOADER_DEPENDENCIES = boost libcurl libtidy jsoncpp rhash tinyxml2

LGOGDOWNLOADER_SUPPORTS_IN_SOURCE_BUILD = NO

LGOGDOWNLOADER_CONF_OPTS  = -DCMAKE_BUILD_TYPE=Release
LGOGDOWNLOADER_CONF_OPTS += -DBUILD_SHARED_LIBS=FALSE

LGOGDOWNLOADER_CONF_ENV += LDFLAGS=-lpthread

$(eval $(cmake-package))
