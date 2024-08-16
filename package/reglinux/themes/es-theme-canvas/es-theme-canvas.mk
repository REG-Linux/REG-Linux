################################################################################
#
# EmulationStation theme "Canvas"
#
################################################################################
# Version.: Commits on Aug 16, 2024
ES_THEME_CANVAS_VERSION = 490c2b463454bc25c9a11c80e05c298aa1f6f433
ES_THEME_CANVAS_SITE = $(call github,REG-Linux,es-theme-canvas,$(ES_THEME_CANVAS_VERSION))

define ES_THEME_CANVAS_INSTALL_TARGET_CMDS
    mkdir -p $(TARGET_DIR)/usr/share/emulationstation/themes/es-theme-canvas
    cp -r $(@D)/* $(TARGET_DIR)/usr/share/emulationstation/themes/es-theme-canvas
endef

$(eval $(generic-package))
