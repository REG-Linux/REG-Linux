################################################################################
#
# EmulationStation theme "Canvas"
#
################################################################################

ifeq ($(BR2_PACKAGE_REGLINUX_RELEASE),y)
ES_THEME_CANVAS_VERSION = v1.7.2
ES_THEME_CANVAS_SITE = https://github.com/REG-Linux/es-theme-canvas/releases/download/$(ES_THEME_CANVAS_VERSION)
ES_THEME_CANVAS_SOURCE = canvas-theme-$(ES_THEME_CANVAS_VERSION).tar.gz
else
# REGStation
ES_THEME_CANVAS_VERSION = d1ffde3fc524f11810d8f93394d71165220923ab
ES_THEME_CANVAS_SITE = $(call github,REG-Linux,es-theme-canvas,$(ES_THEME_CANVAS_VERSION))
endif

define ES_THEME_CANVAS_INSTALL_TARGET_CMDS
    mkdir -p $(TARGET_DIR)/usr/share/emulationstation/themes/es-theme-canvas
    cp -r $(@D)/* $(TARGET_DIR)/usr/share/emulationstation/themes/es-theme-canvas
endef

$(eval $(generic-package))
