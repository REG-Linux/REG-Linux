################################################################################
#
# gamecontrollerdb
#
################################################################################

GAMECONTROLLERDB_VERSION = 2cdd7d4ac38a43d8ca39511e961ac43fbc9f014f
GAMECONTROLLERDB_SITE = $(call github,REG-Linux,SDL_GameControllerDB,$(GAMECONTROLLERDB_VERSION))
GAMECONTROLLERDB_LICENSE = zlib/libpng
GAMECONTROLLERDB_LICENSE_FILES = LICENSE

GAMECONTROLLERDB_PATH = $(TARGET_DIR)/usr/share/regstation

# Install the two pre-split SDL gamecontroller DB lanes verbatim.
#
# All processing — append add_gamecontrollerdb.txt, keep Linux only (field-
# anchored on the platform: token), dedup by GUID, and split the SDL2-HIDAPI
# rows out — now happens upstream in the fork's CI
# (REG-Linux/SDL_GameControllerDB/.github/workflows/gamecontrollerdb.yaml),
# which commits BOTH files to the repo:
#   * gamecontrollerdb.txt       — joydev + SDL3-HIDAPI mappings
#   * gamecontrollerdb-SDL2.txt  — SDL2-HIDAPI mappings (driver-sig 'h' at GUID
#                                  chars 29-30, dpad-as-buttons), read only by
#                                  SDL2 emulators — regmsg appends it last so it
#                                  wins the same-GUID USB collision over the
#                                  SDL3-HIDAPI row in the main file.
# So the package just copies them — no install-time strip.
#
# NOTE: this requires GAMECONTROLLERDB_VERSION above to point at a commit
# produced by the updated CI (one that ships gamecontrollerdb-SDL2.txt with the
# lanes already split). Bump the pin when that commit lands.
#
# See package/controllers/gamecontrollerdb/CONTROLLER-MAPPING-DESIGN.md.
define GAMECONTROLLERDB_INSTALL_TARGET_CMDS
	$(INSTALL) -D -m 644 $(@D)/gamecontrollerdb.txt      $(GAMECONTROLLERDB_PATH)/gamecontrollerdb.txt
	$(INSTALL) -D -m 644 $(@D)/gamecontrollerdb-SDL2.txt $(GAMECONTROLLERDB_PATH)/gamecontrollerdb-SDL2.txt
endef

$(eval $(generic-package))
