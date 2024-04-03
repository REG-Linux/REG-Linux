################################################################################
#
# EmulationStation theme "Carbon"
#
################################################################################
# Version.: Commits on Mar 27, 2024
ES_THEME_CARBON_VERSION = 932bfd288c90dbd229d9e6043430e8ba1c41f41d
ES_THEME_CARBON_SITE = $(call github,REG-Linux,es-theme-carbon,$(ES_THEME_CARBON_VERSION))

define ES_THEME_CARBON_INSTALL_TARGET_CMDS
    mkdir -p $(TARGET_DIR)/usr/share/emulationstation/themes/es-theme-carbon
    cp -r $(@D)/* $(TARGET_DIR)/usr/share/emulationstation/themes/es-theme-carbon
endef

$(eval $(generic-package))
