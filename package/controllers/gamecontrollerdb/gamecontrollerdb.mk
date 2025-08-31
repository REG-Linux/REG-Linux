################################################################################
#
# gamecontrollerdb
#
################################################################################

# Version.: Commits on Aug 25, 2025
GAMECONTROLLERDB_VERSION = 5608aafb948876fea606d3d8f11d7a36eab5e400
GAMECONTROLLERDB_SITE = $(call github,REG-Linux,SDL_GameControllerDB,$(GAMECONTROLLERDB_VERSION))

GAMECONTROLLERDB_PATH = $(TARGET_DIR)/usr/share/emulationstation

define GAMECONTROLLERDB_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/gamecontrollerdb.txt $(GAMECONTROLLERDB_PATH)/gamecontrollerdb.txt
endef

$(eval $(generic-package))
