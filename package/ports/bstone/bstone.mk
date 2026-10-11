################################################################################
#
# bstone
#
################################################################################

BSTONE_VERSION = v1.3.4
BSTONE_SITE = $(call github,bibendovsky,bstone,$(BSTONE_VERSION))

BSTONE_DEPENDENCIES = openal sdl2
BSTONE_LICENSE = GPLv2 & MIT
BSTONE_LICENSE_FILE = LICENSE.txt
BSTONE_SUPPORTS_IN_SOURCE_BUILD = NO

BSTONE_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release
BSTONE_CONF_OPTS += -DBUILD_SHARED_LIBS=OFF
BSTONE_CONF_OPTS += -DCMAKE_INSTALL_PREFIX="/usr/bin"

$(eval $(cmake-package))
