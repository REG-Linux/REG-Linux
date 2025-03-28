################################################################################
#
# bstone
#
################################################################################
# Version: Release 1.2.15 on Mar 22, 2025
BSTONE_VERSION = v1.2.15
BSTONE_SITE = $(call github,bibendovsky,bstone,$(BSTONE_VERSION))

BSTONE_DEPENDENCIES = sdl2
BSTONE_LICENSE = MIT
BSTONE_SUPPORTS_IN_SOURCE_BUILD = NO

BSTONE_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release

$(eval $(cmake-package))
