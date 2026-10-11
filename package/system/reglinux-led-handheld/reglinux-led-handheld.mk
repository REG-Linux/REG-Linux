################################################################################
#
# reglinux-led-handheld
#
################################################################################

# branch: main
REGLINUX_LED_HANDHELD_VERSION = 2703a1941abe13b2b59ec4eb43a396a2872bff8a
REGLINUX_LED_HANDHELD_SITE = $(call github,REG-Linux,reglinux-led-handheld,$(REGLINUX_LED_HANDHELD_VERSION))
REGLINUX_LED_HANDHELD_LICENSE = GPL-3.0-or-later
REGLINUX_LED_HANDHELD_LICENSE_FILES = LICENSE

RUSTC_TARGET_PROFILE = $(if $(BR2_ENABLE_DEBUG),debug,release)
REGLINUX_LED_HANDHELD_LOCATION = target/$(RUSTC_TARGET_NAME)/$(RUSTC_TARGET_PROFILE)

REGLINUX_LED_HANDHELD_PATH = $(BR2_EXTERNAL_REGLINUX_PATH)/package/system/reglinux-led-handheld

define REGLINUX_LED_HANDHELD_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/$(REGLINUX_LED_HANDHELD_LOCATION)/reglinux-led-handheld \
		$(TARGET_DIR)/usr/bin/reglinux-led-handheld
	$(INSTALL) -m 0755 -D $(REGLINUX_LED_HANDHELD_PATH)/S51led-handheld \
		$(TARGET_DIR)/etc/init.d/S51led-handheld
endef

$(eval $(cargo-package))
