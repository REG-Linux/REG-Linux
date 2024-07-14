################################################################################
#
# EmulationStation theme "Neutral"
#
################################################################################
# Version.: Commits on Jul 14, 2024
ES_THEME_NEUTRAL_VERSION = aead9791c0542191ef0da5aa678d483f1f19663f
ES_THEME_NEUTRAL_SITE = $(call github,REG-Linux,es-theme-neutral,$(ES_THEME_NEUTRAL_VERSION))

define ES_THEME_NEUTRAL_INSTALL_TARGET_CMDS
    mkdir -p $(TARGET_DIR)/usr/share/emulationstation/themes/es-theme-neutral
    cp -r $(@D)/* $(TARGET_DIR)/usr/share/emulationstation/themes/es-theme-neutral
endef

$(eval $(generic-package))
