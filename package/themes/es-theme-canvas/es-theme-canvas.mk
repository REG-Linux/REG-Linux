################################################################################
#
# EmulationStation theme "Canvas"
#
################################################################################

ES_THEME_CANVAS_VERSION = 6c19914e60294c725d5e71b00c983211a7c5618d
ES_THEME_CANVAS_SITE = $(call github,REG-Linux,es-theme-canvas,$(ES_THEME_CANVAS_VERSION))

define ES_THEME_CANVAS_INSTALL_TARGET_CMDS
    mkdir -p $(TARGET_DIR)/usr/share/emulationstation/themes/es-theme-canvas
    cp -r $(@D)/* $(TARGET_DIR)/usr/share/emulationstation/themes/es-theme-canvas
endef

$(eval $(generic-package))
