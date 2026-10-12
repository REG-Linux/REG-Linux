################################################################################
#
# reglinux-compat — hardware compatibility probe and reporting
#
################################################################################

REGLINUX_COMPAT_VERSION = 1
REGLINUX_COMPAT_LICENSE = GPL
REGLINUX_COMPAT_SOURCE =

REGLINUX_COMPAT_PATH = $(BR2_EXTERNAL_REGLINUX_PATH)/package/system/reglinux-compat

define REGLINUX_COMPAT_INSTALL_TARGET_CMDS
	# Scripts
	mkdir -p $(TARGET_DIR)/usr/bin
	install -m 0755 $(REGLINUX_COMPAT_PATH)/scripts/reg-compat-probe   $(TARGET_DIR)/usr/bin/
	install -m 0755 $(REGLINUX_COMPAT_PATH)/scripts/reg-compat-sync    $(TARGET_DIR)/usr/bin/
	install -m 0755 $(REGLINUX_COMPAT_PATH)/scripts/reg-compat-resume  $(TARGET_DIR)/usr/bin/

	# Init script (runs at boot after network)
	mkdir -p $(TARGET_DIR)/etc/init.d
	install -m 0755 $(REGLINUX_COMPAT_PATH)/S98compat $(TARGET_DIR)/etc/init.d/

	# udev rules (network sync + hardware hotplug re-probe)
	mkdir -p $(TARGET_DIR)/etc/udev/rules.d
	install -m 0644 $(REGLINUX_COMPAT_PATH)/rules/99-compat-net.rules  $(TARGET_DIR)/etc/udev/rules.d/
	install -m 0644 $(REGLINUX_COMPAT_PATH)/rules/99-compat-hw.rules   $(TARGET_DIR)/etc/udev/rules.d/
endef

$(eval $(generic-package))
