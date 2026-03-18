################################################################################
#
# switch-bsp
#
# Nintendo Switch Board Support Package for REG-Linux
# Based on Lakka-LibreELEC's switch-bsp package
#
################################################################################

SWITCH_BSP_VERSION = 1.3
SWITCH_BSP_SOURCE =
SWITCH_BSP_LICENSE = GPL-2.0+
SWITCH_BSP_DEPENDENCIES = usb-gadget-scripts

define SWITCH_BSP_INSTALL_TARGET_CMDS
	# Install scripts
	$(INSTALL) -D -m 0755 $(SWITCH_BSP_PKGDIR)/scripts/pair-joycon.sh \
		$(TARGET_DIR)/usr/bin/pair-joycon.sh
	$(INSTALL) -D -m 0755 $(SWITCH_BSP_PKGDIR)/scripts/dock-hotplug \
		$(TARGET_DIR)/usr/bin/dock-hotplug
	$(INSTALL) -D -m 0755 $(SWITCH_BSP_PKGDIR)/scripts/fix-sysfs-permissions.sh \
		$(TARGET_DIR)/usr/bin/fix-sysfs-permissions.sh

	# Install ALSA UCM2 data for Tegra audio
	mkdir -p $(TARGET_DIR)/usr/share/alsa/ucm2/tegra-snd-t210r
	$(INSTALL) -D -m 0644 $(SWITCH_BSP_PKGDIR)/ucm_data/tegra-snd-t210r/tegra-snd-t210r.conf \
		$(TARGET_DIR)/usr/share/alsa/ucm2/tegra-snd-t210r/tegra-snd-t210r.conf
	$(INSTALL) -D -m 0644 $(SWITCH_BSP_PKGDIR)/ucm_data/tegra-snd-t210r/HiFi.conf \
		$(TARGET_DIR)/usr/share/alsa/ucm2/tegra-snd-t210r/HiFi.conf
endef

$(eval $(generic-package))
