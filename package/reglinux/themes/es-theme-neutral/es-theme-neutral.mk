################################################################################
#
# EmulationStation theme "Neutral"
#
################################################################################
# Version.: Commits on Jul 11, 2024
ES_THEME_NEUTRAL_VERSION = a74d66f9c557ac5dfb3b1ae5ea9542170337bc47
ES_THEME_NEUTRAL_SITE = $(call github,REG-Linux,es-theme-neutral,$(ES_THEME_NEUTRAL_VERSION))

define ES_THEME_NEUTRAL_INSTALL_TARGET_CMDS
    mkdir -p $(TARGET_DIR)/usr/share/emulationstation/themes/es-theme-neutral
    cp -r $(@D)/* $(TARGET_DIR)/usr/share/emulationstation/themes/es-theme-neutral
endef

$(eval $(generic-package))
