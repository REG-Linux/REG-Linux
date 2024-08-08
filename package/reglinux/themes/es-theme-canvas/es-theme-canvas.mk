################################################################################
#
# EmulationStation theme "Canvas"
#
################################################################################
# Version.: Commits on Aug 08, 2024
ES_THEME_CANVAS_VERSION = 8d0d8f6d72da2472dba0f0db2b8a961bd001508a
ES_THEME_CANVAS_SITE = $(call github,REG-Linux,es-theme-canvas,$(ES_THEME_CANVAS_VERSION))

define ES_THEME_CANVAS_INSTALL_TARGET_CMDS
    mkdir -p $(TARGET_DIR)/usr/share/emulationstation/themes/es-theme-canvas
    cp -r $(@D)/* $(TARGET_DIR)/usr/share/emulationstation/themes/es-theme-canvas
endef

$(eval $(generic-package))
