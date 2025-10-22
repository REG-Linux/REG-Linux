################################################################################
#
# nghttp3
#
################################################################################
NGHTTP3_VERSION = v1.12.0
NGHTTP3_SITE = https://github.com/ngtcp2/nghttp3.git
NGHTTP3_SITE_METHOD = git
NGHTTP3_GIT_SUBMODULES = YES
NGHTTP3_LICENSE = MIT

NGHTTP3_SUPPORTS_IN_SOURCE_BUILD = NO
NGHTTP3_INSTALL_STAGING = YES

NGHTTP3_CONF_OPTS  = -DCMAKE_BUILD_TYPE=Release
NGHTTP3_CONF_OPTS += -DBUILD_STATIC_LIBS=TRUE
NGHTTP3_CONF_OPTS += -DBUILD_SHARED_LIBS=FALSE

NGHTTP3_CONF_ENV += LDFLAGS=-lpthread

$(eval $(cmake-package))
