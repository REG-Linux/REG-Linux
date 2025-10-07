################################################################################
#
# gamecontrollerdb
#
################################################################################

# Version.: Commits on Oct 6, 2025
GAMECONTROLLERDB_VERSION = e9a4edaea0f5b8b91291c44db1ff5cb1983ad6b8
GAMECONTROLLERDB_SITE = $(call github,REG-Linux,SDL_GameControllerDB,$(GAMECONTROLLERDB_VERSION))

GAMECONTROLLERDB_PATH = $(TARGET_DIR)/usr/share/emulationstation

define GAMECONTROLLERDB_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/gamecontrollerdb.txt $(GAMECONTROLLERDB_PATH)/gamecontrollerdb.txt
endef

$(eval $(generic-package))
