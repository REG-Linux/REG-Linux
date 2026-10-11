################################################################################
#
# openfodder — Cannon Fodder engine reimplementation
#
################################################################################

OPENFODDER_VERSION = 2.0.0
OPENFODDER_SITE = $(call github,OpenFodder,openfodder,$(OPENFODDER_VERSION))
OPENFODDER_LICENSE = GPL-3.0
OPENFODDER_LICENSE_FILES = LICENSE

OPENFODDER_DEPENDENCIES = sdl2 sdl2_mixer

OPENFODDER_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release
OPENFODDER_CONF_OPTS += -DBUILD_SHARED_LIBS=OFF
OPENFODDER_CONF_OPTS += -DBUILD_STATIC_LIBS=ON

define OPENFODDER_INSTALL_TARGET_CMDS
	$(INSTALL) -D -m 0755 $(@D)/openfodder $(TARGET_DIR)/usr/bin/openfodder
endef

$(eval $(cmake-package))
