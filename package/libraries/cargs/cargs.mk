################################################################################
#
# cargs
#
################################################################################
# Version 1.2.0 released on Jun 19, 2024
CARGS_VERSION = v1.2.0
CARGS_SITE = $(call github,likle,cargs,$(CARGS_VERSION))
CARGS_LICENSE = MIT
CARGS_LICENSE_FILES = LICENSE
CARGS_DEPENDENCIES =
CARGS_SUPPORTS_IN_SOURCE_BUILD = NO

CARGS_CONF_OPTS += -DBUILD_SHARED_LIBS=On -DCMAKE_BUILD_TYPE=Release

CARGS_INSTALL_STAGING = YES

$(eval $(cmake-package))
