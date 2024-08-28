################################################################################
#
# gamemode
#
################################################################################
GAMEMODE_VERSION = 1.8.2
GAMEMODE_SITE = $(call github,FeralInteractive,gamemode,$(GAMEMODE_VERSION))
GAMEMODE_INSTALL_STAGING = YES

GAMEMODE_CONF_OPTS = -Dwith-sd-bus-provider=no-daemon -Dwith-examples=false

$(eval $(meson-package))
