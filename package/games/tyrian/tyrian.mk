################################################################################
#
# TYRIAN
#
################################################################################
# Version: Release from Sep 13, 2026
TYRIAN_VERSION = v2.1.20260913
TYRIAN_SITE = $(call github,opentyrian,opentyrian,$(TYRIAN_VERSION))

TYRIAN_DEPENDENCIES = sdl2 sdl2_net

define TYRIAN_BUILD_CMDS
	# Cross-compile
	cd $(@D) && \
	CC="$(TARGET_CC)" \
	CXX="$(TARGET_CXX)" \
	PREFIX="$(STAGING_DIR)/usr" \
        PKG_CONFIG="$(HOST_DIR)/usr/bin/pkg-config --define-prefix" \
        PKG_CONFIG_PATH="$(STAGING_DIR)/usr/lib/pkgconfig" \
	CPPFLAGS="-I$(STAGING_DIR)/usr/include -I$(STAGING_DIR)/usr/include/SDL2 -lSDL2" \
	$(MAKE) PREFIX="$(STAGING_DIR)/usr"
endef

define TYRIAN_INSTALL_TARGET_CMDS
	$(INSTALL) -D -m 0755 $(@D)/opentyrian $(TARGET_DIR)/usr/bin/
endef

$(eval $(generic-package))
