################################################################################
#
# gamemode
#
################################################################################
GAMEMODE_VERSION = 1.8.2
GAMEMODE_SITE = $(call github,FeralInteractive,gamemode,$(GAMEMODE_VERSION))
GAMEMODE_INSTALL_STAGING = YES
GAMEMODE_DEPENDENCIES = dbus basu inih

GAMEMODE_CONF_OPTS = -Dwith-sd-bus-provider=basu
GAMEMODE_CONF_OPTS += -Dwith-examples=false

# REG comments
# gamemode.conf should be copied to /etc/dbus-1/system.d/gamemode.conf
# Yes, even if not using systemd

define GAMEMODE_INSTALL_CONFIG
	mkdir -p $(TARGET_DIR)/etc/dbus-1/system.d
	cp $(BR2_EXTERNAL_REGLINUX_PATH)/package/libraries/gamemode/gamemode.conf $(TARGET_DIR)/etc/dbus-1/system.d/gamemode.conf
endef

GAMEMODE_POST_INSTALL_TARGET_HOOKS += GAMEMODE_INSTALL_CONFIG

$(eval $(meson-package))
