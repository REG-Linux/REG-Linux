################################################################################
#
# kmsvnc
#
################################################################################
KMSVNC_VERSION = 190db24b727e556e234497c1ce38b88cd6668544
KMSVNC_SITE = https://github.com/isjerryxiao/kmsvnc.git
KMSVNC_SITE_METHOD = git
KMSVNC_LICENSE = GPL-3.0
KMSVNC_DEPENDENCIES = libdrm

KMSVNC_SUPPORTS_IN_SOURCE_BUILD = NO

KMSVNC_CONF_OPTS  = -DCMAKE_BUILD_TYPE=Release
KMSVNC_CONF_OPTS += -DBUILD_SHARED_LIBS=FALSE

KMSVNC_CONF_ENV += LDFLAGS=-lpthread

$(eval $(cmake-package))
