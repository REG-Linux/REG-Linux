################################################################################
#
# hypseus-singe
#
################################################################################

HYPSEUS_SINGE_VERSION = v3.0.2
HYPSEUS_SINGE_SITE =  $(call github,DirtBagXon,hypseus-singe,$(HYPSEUS_SINGE_VERSION))
HYPSEUS_SINGE_LICENSE = GPLv3

HYPSEUS_SINGE_DEPENDENCIES = libzip sdl3 sdl3_image sdl3_mixer sdl3_ttf zlib libogg libvorbis libmpeg2

HYPSEUS_SINGE_SUBDIR = build
HYPSEUS_SINGE_CONF_OPTS = ../src -DBUILD_SHARED_LIBS=OFF

define HYPSEUS_SINGE_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/build/hypseus $(TARGET_DIR)/usr/bin/
		mkdir -p $(TARGET_DIR)/usr/share/hypseus-singe

	# copy support files
	cp -pr $(@D)/pics $(TARGET_DIR)/usr/share/hypseus-singe
	cp -pr $(@D)/fonts $(TARGET_DIR)/usr/share/hypseus-singe
	cp -pr $(@D)/sound $(TARGET_DIR)/usr/share/hypseus-singe
	cp -pf $(@D)/doc/*.ini $(TARGET_DIR)/usr/share/hypseus-singe
endef

$(eval $(cmake-package))
