################################################################################
#
# firmware-radxa-rkwifibt
#
################################################################################

FIRMWARE_RADXA_RKWIFIBT_VERSION = bfac4bf73d98a114d7ad5f91e10789f7fda985a6
FIRMWARE_RADXA_RKWIFIBT_SITE = $(call github,REG-Linux,firmware-radxa-wifi-bt,$(FIRMWARE_RADXA_RKWIFIBT_VERSION))

# - rtl8821cs firmware is installed -- these were provided as part of the Indiedroid Nova BSP
# - rtk_hciattach is patched to be compatible from the above firmware and then built and installed.
# - bt_load_rtk_firmware is a script that:
#   1. powercycles the bluetooth adapter
#   2. runs the userspace rtk_hciattach utility
#   3. runs hciconfig hci0 up
# - S29rtk_bt is a startup script that runs the firmware loader but only when the 8821CS card is present

FIRMWARE_RADXA_RKWIFIBT_FIRMWARE_DIR = $(TARGET_DIR)/lib/firmware/rtl_bt
define FIRMWARE_RADXA_RKWIFIBT_BUILD_CMDS
	$(MAKE) $(TARGET_CONFIGURE_OPTS) -C $(@D)/realtek/rtk_hciattach
endef

define FIRMWARE_RADXA_RKWIFIBT_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/lib/firmware/rtl_bt
	$(INSTALL) -m 0644 -D $(FIRMWARE_RADXA_RKWIFIBT_PKGDIR)/rtl8821cs/rtl8821cs_config $(FIRMWARE_RADXA_RKWIFIBT_FIRMWARE_DIR)/rtl8821cs_config
	$(INSTALL) -m 0644 -D $(FIRMWARE_RADXA_RKWIFIBT_PKGDIR)/rtl8821cs/rtl8821cs_fw $(FIRMWARE_RADXA_RKWIFIBT_FIRMWARE_DIR)/rtl8821cs_fw
	$(INSTALL) -m 0755 -D $(@D)/realtek/rtk_hciattach/rtk_hciattach $(TARGET_DIR)/usr/bin/rtk_hciattach
	$(INSTALL) -m 0755 -D $(@D)/bt_load_rtk_firmware $(TARGET_DIR)/usr/bin/bt_load_rtk_firmware
	$(INSTALL) -m 0755 -D $(FIRMWARE_RADXA_RKWIFIBT_PKGDIR)/S29rtk_bt $(TARGET_DIR)/etc/init.d/S29rtk_bt
	# install the AP6275P wifi firmware
	mkdir -p $(TARGET_DIR)/lib/firmware/ap6275p
	$(INSTALL) -m 0644 -D $(@D)/firmware/broadcom/AP6275P/wifi/* $(TARGET_DIR)/lib/firmware/ap6275p
	# install the AP6275P BT firmware
	mkdir -p $(TARGET_DIR)/lib/firmware/brcm
	$(INSTALL) -m 0644 -D $(@D)/firmware/broadcom/AP6275P/bt/BCM4362A2.hcd $(TARGET_DIR)/lib/firmware/brcm
	ln -sf /lib/firmware/brcm/BCM4362A2.hcd $(TARGET_DIR)/lib/firmware/ap6275p/BCM4362A2.hcd
endef

$(eval $(generic-package))
