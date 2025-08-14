################################################################################
#
# gamecontrollerdb
#
################################################################################

GAMECONTROLLERDB_VERSION = 816d047ad4c33efe3195eaa63b4eb72fd3d8fa51
GAMECONTROLLERDB_SITE = $(call github,REG-Linux,SDL_GameControllerDB,$(GAMECONTROLLERDB_VERSION))

GAMECONTROLLERDB_PATH = $(TARGET_DIR)/usr/share/emulationstation

define GAMECONTROLLERDB_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/gamecontrollerdb.txt $(GAMECONTROLLERDB_PATH)/gamecontrollerdb.txt
endef

$(eval $(generic-package))
