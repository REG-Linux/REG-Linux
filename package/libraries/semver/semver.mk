################################################################################
#
# semver
#
################################################################################
SEMVER_VERSION = v1.0.0-rc
SEMVER_SITE = $(call github,Neargye,semver,$(SEMVER_VERSION))
SEMVER_LICENSE = MIT

SEMVER_SUPPORTS_IN_SOURCE_BUILD = NO
SEMVER_INSTALL_STAGING = YES

SEMVER_CONF_OPTS  = -DCMAKE_BUILD_TYPE=Release

$(eval $(cmake-package))
