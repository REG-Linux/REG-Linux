################################################################################
#
# EmulationStation theme "Canvas"
#
################################################################################

ES_THEME_CANVAS_VERSION = 02e295bd6718b7aa476389fb9fbe45a33853f120
ES_THEME_CANVAS_SITE = $(call github,REG-Linux,es-theme-canvas,$(ES_THEME_CANVAS_VERSION))

define ES_THEME_CANVAS_INSTALL_TARGET_CMDS
    mkdir -p $(TARGET_DIR)/usr/share/emulationstation/themes/es-theme-canvas
    cp -r $(@D)/* $(TARGET_DIR)/usr/share/emulationstation/themes/es-theme-canvas
endef

$(eval $(generic-package))
