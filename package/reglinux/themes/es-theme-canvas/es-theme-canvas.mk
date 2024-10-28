################################################################################
#
# EmulationStation theme "Canvas"
#
################################################################################

ES_THEME_CANVAS_VERSION = 1c2e8455df9fe8e688ef079d7f32473537d99d1b
ES_THEME_CANVAS_SITE = $(call github,REG-Linux,es-theme-canvas,$(ES_THEME_CANVAS_VERSION))

define ES_THEME_CANVAS_INSTALL_TARGET_CMDS
    mkdir -p $(TARGET_DIR)/usr/share/emulationstation/themes/es-theme-canvas
    cp -r $(@D)/* $(TARGET_DIR)/usr/share/emulationstation/themes/es-theme-canvas
endef

$(eval $(generic-package))
