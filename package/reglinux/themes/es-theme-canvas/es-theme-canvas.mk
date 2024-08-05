################################################################################
#
# EmulationStation theme "Canvas"
#
################################################################################
# Version.: Commits on Aug 04, 2024
ES_THEME_CANVAS_VERSION = c948b85531ad90df8f9fc869910ed038f9a3aff0
ES_THEME_CANVAS_SITE = $(call github,REG-Linux,es-theme-canvas,$(ES_THEME_CANVAS_VERSION))

define ES_THEME_CANVAS_INSTALL_TARGET_CMDS
    mkdir -p $(TARGET_DIR)/usr/share/emulationstation/themes/es-theme-canvas
    cp -r $(@D)/* $(TARGET_DIR)/usr/share/emulationstation/themes/es-theme-canvas
endef

$(eval $(generic-package))
