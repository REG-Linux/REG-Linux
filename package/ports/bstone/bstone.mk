################################################################################
#
# bstone
#
################################################################################
# Version: Release 1.3.1 on Dec 25, 2025
BSTONE_VERSION = v1.3.1
BSTONE_SITE = $(call github,bibendovsky,bstone,$(BSTONE_VERSION))

BSTONE_DEPENDENCIES = openal sdl2
BSTONE_LICENSE = GPLv2 & MIT
BSTONE_LICENSE_FILE = LICENSE.txt
BSTONE_SUPPORTS_IN_SOURCE_BUILD = NO

BSTONE_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release
BSTONE_CONF_OPTS += -DBUILD_SHARED_LIBS=OFF
BSTONE_CONF_OPTS += -DCMAKE_INSTALL_PREFIX="/usr/bin"

define BSTONE_EVMAPY
	mkdir -p $(TARGET_DIR)/usr/share/evmapy
	cp $(BR2_EXTERNAL_REGLINUX_PATH)/package/ports/bstone/bstone.keys \
	    $(TARGET_DIR)/usr/share/evmapy
endef

BSTONE_POST_INSTALL_TARGET_HOOKS += BSTONE_EVMAPY

$(eval $(cmake-package))
