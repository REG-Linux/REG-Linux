################################################################################
#
# reglinux usbgadget
#
################################################################################

REGLINUX_USBGADGET_VERSION = 1
REGLINUX_USBGADGET_SOURCE=

define REGLINUX_USBGADGET_INSTALL_TARGET_CMDS
    $(INSTALL) -Dm755 $(REGLINUX_USBGADGET_PKGDIR)/scripts/S13usbgadget     $(TARGET_DIR)/etc/init.d/S13usbgadget
    $(INSTALL) -Dm755 $(REGLINUX_USBGADGET_PKGDIR)/scripts/usbgadget        $(TARGET_DIR)/usr/bin/usbgadget
    $(INSTALL) -Dm755 $(REGLINUX_USBGADGET_PKGDIR)/services/USB_GADGET_ADB  $(TARGET_DIR)/usr/share/reglinux/services/USB_GADGET_ADB
    $(INSTALL) -Dm755 $(REGLINUX_USBGADGET_PKGDIR)/services/USB_GADGET      $(TARGET_DIR)/usr/share/reglinux/services/USB_GADGET
    $(INSTALL) -Dm644 $(REGLINUX_USBGADGET_PKGDIR)/rules/80-usbgadget.rules $(TARGET_DIR)/etc/udev/rules.d/80-usbgadget.rules
endef

$(eval $(generic-package))
