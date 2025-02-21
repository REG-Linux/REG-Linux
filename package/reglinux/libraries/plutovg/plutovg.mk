################################################################################
#
# plutovg
#
################################################################################
PLUTOVG_VERSION = v0.0.12
PLUTOVG_SITE = https://github.com/sammycage/plutovg
PLUTOVG_SITE_METHOD = git
PLUTOVG_LICENSE = MIT

PLUTOVG_SUPPORTS_IN_SOURCE_BUILD = NO
PLUTOVG_INSTALL_STAGING = YES

PLUTOVG_CONF_OPTS  = -DCMAKE_BUILD_TYPE=Release
PLUTOVG_CONF_OPTS += -DBUILD_SHARED_LIBS=TRUE

PLUTOVG_CONF_ENV += LDFLAGS=-lpthread

$(eval $(cmake-package))
