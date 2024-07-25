################################################################################
#
# EmulationStation theme "Neutral"
#
################################################################################
# Version.: Commits on Jul 16, 2024
ES_THEME_NEUTRAL_VERSION = 0d1df7a5deb57dc55bba50172b674d8308f11737
ES_THEME_NEUTRAL_SITE = $(call github,REG-Linux,es-theme-neutral,$(ES_THEME_NEUTRAL_VERSION))

define ES_THEME_NEUTRAL_INSTALL_TARGET_CMDS
    mkdir -p $(TARGET_DIR)/usr/share/emulationstation/themes/es-theme-neutral
    cp -r $(@D)/* $(TARGET_DIR)/usr/share/emulationstation/themes/es-theme-neutral
endef

$(eval $(generic-package))
