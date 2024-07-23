################################################################################
#
# EmulationStation theme "Canvas"
#
################################################################################
# Version.: Commits on Jul 23, 2024
ES_THEME_CANVAS_VERSION = 55e318876116e9342a9b99f6557be0ce28a6e5e2
ES_THEME_CANVAS_SITE = $(call github,REG-Linux,es-theme-canvas,$(ES_THEME_CANVAS_VERSION))

define ES_THEME_CANVAS_INSTALL_TARGET_CMDS
    mkdir -p $(TARGET_DIR)/usr/share/emulationstation/themes/es-theme-canvas
    cp -r $(@D)/* $(TARGET_DIR)/usr/share/emulationstation/themes/es-theme-canvas
endef

$(eval $(generic-package))
