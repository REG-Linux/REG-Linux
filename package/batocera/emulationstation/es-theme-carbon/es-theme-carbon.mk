################################################################################
#
# EmulationStation theme "Carbon"
#
################################################################################
# Version.: Commits on Apr 25, 2024
ES_THEME_CARBON_VERSION = 22ee6c52e78c91f6297acabca1bf590cc15bbf24
ES_THEME_CARBON_SITE = $(call github,REG-Linux,es-theme-carbon,$(ES_THEME_CARBON_VERSION))

define ES_THEME_CARBON_INSTALL_TARGET_CMDS
    mkdir -p $(TARGET_DIR)/usr/share/emulationstation/themes/es-theme-carbon
    cp -r $(@D)/* $(TARGET_DIR)/usr/share/emulationstation/themes/es-theme-carbon
endef

$(eval $(generic-package))
