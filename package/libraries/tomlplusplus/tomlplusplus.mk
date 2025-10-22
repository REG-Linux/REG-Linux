################################################################################
#
# tomlplusplus
#
################################################################################
TOMLPLUSPLUS_VERSION = v3.4.0
TOMLPLUSPLUS_SITE = $(call github,marzer,tomlplusplus,$(TOMLPLUSPLUS_VERSION))
TOMLPLUSPLUS_LICENSE = MIT

TOMLPLUSPLUS_SUPPORTS_IN_SOURCE_BUILD = NO
TOMLPLUSPLUS_INSTALL_STAGING = YES
TOMLPLUSPLUS_INSTALL_TARGET = NO

TOMLPLUSPLUS_CONF_OPTS  = -DCMAKE_BUILD_TYPE=Release

$(eval $(cmake-package))
