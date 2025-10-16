################################################################################
#
# RGBDS
#
################################################################################
RGBDS_VERSION = v0.9.1
RGBDS_SITE = $(call github,gbdev,rgbds,$(RGBDS_VERSION))
RGBDS_LICENSE = MIT
RGBDS_SUPPORTS_IN_SOURCE_BUILD = NO

HOST_RGBDS_DEPENDENCIES = host-libpng host-bison
HOST_RGBDS_CONF_OPTS  = -DCMAKE_BUILD_TYPE=Release
HOST_RGBDS_CONF_OPTS += -DBUILD_SHARED_LIBS=FALSE
HOST_RGBDS_CONF_ENV += LDFLAGS=-lpthread

$(eval $(host-cmake-package))
