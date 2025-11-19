################################################################################
#
# EmulationStation theme "Canvas"
#
################################################################################

ES_THEME_CANVAS_VERSION = v1.7
ES_THEME_CANVAS_SITE = https://github.com/REG-Linux/es-theme-canvas/releases/download/$(ES_THEME_CANVAS_VERSION)
ES_THEME_CANVAS_SOURCE = canvas-theme-$(ES_THEME_CANVAS_VERSION).tar.gz

define ES_THEME_CANVAS_INSTALL_TARGET_CMDS
    mkdir -p $(TARGET_DIR)/usr/share/emulationstation/themes/es-theme-canvas
    cp -r $(@D)/* $(TARGET_DIR)/usr/share/emulationstation/themes/es-theme-canvas
endef

$(eval $(generic-package))
