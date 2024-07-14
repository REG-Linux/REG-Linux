################################################################################
#
# EmulationStation theme "Neutral"
#
################################################################################
# Version.: Commits on Jul 15, 2024
ES_THEME_NEUTRAL_VERSION = 1d62458419f573e12fc6d062552c1810a5f577b6
ES_THEME_NEUTRAL_SITE = $(call github,REG-Linux,es-theme-neutral,$(ES_THEME_NEUTRAL_VERSION))

define ES_THEME_NEUTRAL_INSTALL_TARGET_CMDS
    mkdir -p $(TARGET_DIR)/usr/share/emulationstation/themes/es-theme-neutral
    cp -r $(@D)/* $(TARGET_DIR)/usr/share/emulationstation/themes/es-theme-neutral
endef

$(eval $(generic-package))
