################################################################################
#
# gamecontrollerdb
#
################################################################################

GAMECONTROLLERDB_VERSION = 74dc9416f6c081240db08eed90e219cbc8efb2c2
GAMECONTROLLERDB_SITE = $(call github,REG-Linux,SDL_GameControllerDB,$(GAMECONTROLLERDB_VERSION))

GAMECONTROLLERDB_PATH = $(TARGET_DIR)/usr/share/emulationstation

define GAMECONTROLLERDB_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/gamecontrollerdb.txt $(GAMECONTROLLERDB_PATH)/gamecontrollerdb.txt
endef

$(eval $(generic-package))
