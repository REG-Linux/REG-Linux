################################################################################
#
# libtidy
#
################################################################################
LIBTIDY_VERSION = 5.8.0
LIBTIDY_SITE = $(call github,htacg,tidy-html5,$(LIBTIDY_VERSION))
LIBTIDY_LICENSE = BSD
LIBTIDY_DEPENDENCIES = boost libcurl jsoncpp rhash

LIBTIDY_SUPPORTS_IN_SOURCE_BUILD = NO
LIBTIDY_INSTALL_STAGING = YES

LIBTIDY_CONF_OPTS  = -DCMAKE_BUILD_TYPE=Release
LIBTIDY_CONF_OPTS += -DBUILD_SHARED_LIBS=FALSE

LIBTIDY_CONF_ENV += LDFLAGS=-lpthread

$(eval $(cmake-package))
