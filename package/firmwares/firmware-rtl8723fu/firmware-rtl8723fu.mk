################################################################################
#
# firmware-rtl8723fu
#
################################################################################
# Bluetooth firmware of the RTL8733BU WiFi/BT combo chip (Miyoo Flip), loaded
# by btrtl as rtl_bt/rtl8723fu_{fw,config}.bin. Not in linux-firmware; from
# ROCKNIX (projects/ROCKNIX/packages/linux-firmware/kernel-firmware/extra-firmware).

FIRMWARE_RTL8723FU_SOURCE =
FIRMWARE_RTL8723FU_LICENSE = PROPRIETARY

define FIRMWARE_RTL8723FU_INSTALL_TARGET_CMDS
	$(INSTALL) -m 0644 -D $(FIRMWARE_RTL8723FU_PKGDIR)/rtl_bt/rtl8723fu_fw.bin \
		$(TARGET_DIR)/lib/firmware/rtl_bt/rtl8723fu_fw.bin
	$(INSTALL) -m 0644 -D $(FIRMWARE_RTL8723FU_PKGDIR)/rtl_bt/rtl8723fu_config.bin \
		$(TARGET_DIR)/lib/firmware/rtl_bt/rtl8723fu_config.bin
endef

$(eval $(generic-package))
