################################################################################
#
# nsync
#
################################################################################
NSYNC_VERSION = 1.30.0
NSYNC_SITE = $(call github,google,nsync,$(NSYNC_VERSION))
#NSYNC_SITE_METHOD = git
#NSYNC_GIT_SUBMODULES = YES
NSYNC_LICENSE = Apache-2.0

NSYNC_SUPPORTS_IN_SOURCE_BUILD = NO
NSYNC_INSTALL_STAGING = YES

NSYNC_CONF_OPTS  = -DCMAKE_BUILD_TYPE=Release
NSYNC_CONF_OPTS += -DBUILD_STATIC_LIBS=TRUE
NSYNC_CONF_OPTS += -DBUILD_SHARED_LIBS=FALSE

NSYNC_CONF_ENV += LDFLAGS=-lpthread

$(eval $(cmake-package))
