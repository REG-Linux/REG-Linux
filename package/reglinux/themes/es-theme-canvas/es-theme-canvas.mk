################################################################################
#
# EmulationStation theme "Canvas"
#
################################################################################
# Version.: Commits on Aug 17, 2024
ES_THEME_CANVAS_VERSION = 17d9ea19a5799772b16fa7320c4000cccb030349
ES_THEME_CANVAS_SITE = $(call github,REG-Linux,es-theme-canvas,$(ES_THEME_CANVAS_VERSION))

define ES_THEME_CANVAS_INSTALL_TARGET_CMDS
    mkdir -p $(TARGET_DIR)/usr/share/emulationstation/themes/es-theme-canvas
    cp -r $(@D)/* $(TARGET_DIR)/usr/share/emulationstation/themes/es-theme-canvas
endef

$(eval $(generic-package))
