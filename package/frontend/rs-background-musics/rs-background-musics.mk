################################################################################
#
# rs-background-musics
#
################################################################################

RS_BACKGROUND_MUSICS_VERSION = 3.0
RS_BACKGROUND_MUSICS_LICENSE = Public Domain
RS_BACKGROUND_MUSICS_SOURCE=

RS_BACKGROUND_MUSICS_PATH = $(BR2_EXTERNAL_REGLINUX_PATH)/package/frontend/rs-background-musics

define RS_BACKGROUND_MUSICS_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/usr/share/reglinux/music
	cp -R $(RS_BACKGROUND_MUSICS_PATH)/music/* $(TARGET_DIR)/usr/share/reglinux/music/
endef

$(eval $(generic-package))
