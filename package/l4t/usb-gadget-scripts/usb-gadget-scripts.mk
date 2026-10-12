################################################################################
#
# usb-gadget-scripts
#
# USB gadget configuration scripts for the Nintendo Switch
# Based on Lakka-LibreELEC's usb-gadget-scripts package
#
################################################################################

USB_GADGET_SCRIPTS_VERSION = 2.0
USB_GADGET_SCRIPTS_SOURCE =
USB_GADGET_SCRIPTS_LICENSE = GPL-2.0+
USB_GADGET_SCRIPTS_DEPENDENCIES = umtp-responder

define USB_GADGET_SCRIPTS_INSTALL_TARGET_CMDS
	$(INSTALL) -D -m 0755 $(USB_GADGET_SCRIPTS_PKGDIR)/usb-gadget.sh \
		$(TARGET_DIR)/usr/bin/usb-gadget.sh
endef

$(eval $(generic-package))
