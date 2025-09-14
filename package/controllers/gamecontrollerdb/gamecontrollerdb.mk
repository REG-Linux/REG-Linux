################################################################################
#
# gamecontrollerdb
#
################################################################################

# Version.: Commits on Sep 13, 2025
GAMECONTROLLERDB_VERSION = ad1750d93ef4ad49fda9b161ac36c00864494f5c
GAMECONTROLLERDB_SITE = $(call github,REG-Linux,SDL_GameControllerDB,$(GAMECONTROLLERDB_VERSION))

GAMECONTROLLERDB_PATH = $(TARGET_DIR)/usr/share/emulationstation

define GAMECONTROLLERDB_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/gamecontrollerdb.txt $(GAMECONTROLLERDB_PATH)/gamecontrollerdb.txt
endef

$(eval $(generic-package))
