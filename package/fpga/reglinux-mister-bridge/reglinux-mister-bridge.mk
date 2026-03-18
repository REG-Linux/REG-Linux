################################################################################
#
# reglinux-mister-bridge
#
################################################################################

REGLINUX_MISTER_BRIDGE_VERSION = 0.1.0
REGLINUX_MISTER_BRIDGE_LICENSE = GPL-2.0+
REGLINUX_MISTER_BRIDGE_SOURCE =

REGLINUX_MISTER_BRIDGE_CARGO_INSTALL_OPTS = --path ./

MISTER_BRIDGE_PKGDIR = $(BR2_EXTERNAL_REGLINUX_PATH)/package/fpga/reglinux-mister-bridge

define REGLINUX_MISTER_BRIDGE_EXTRACT_CMDS
	cp -avf $(MISTER_BRIDGE_PKGDIR)/src/* $(@D)
endef

define REGLINUX_MISTER_BRIDGE_STRIP_BINARY
	$(TARGET_STRIP) -s $(TARGET_DIR)/usr/bin/mister-bridge
endef

define REGLINUX_MISTER_BRIDGE_INSTALL_INIT
	$(INSTALL) -m 0755 -D $(MISTER_BRIDGE_PKGDIR)/S25mister-fpga \
		$(TARGET_DIR)/etc/init.d/S25mister-fpga
	mkdir -p $(TARGET_DIR)/etc/udev/rules.d
	$(INSTALL) -m 0644 -D $(MISTER_BRIDGE_PKGDIR)/99-mister-fpga.rules \
		$(TARGET_DIR)/etc/udev/rules.d/99-mister-fpga.rules
endef

REGLINUX_MISTER_BRIDGE_POST_INSTALL_TARGET_HOOKS += REGLINUX_MISTER_BRIDGE_STRIP_BINARY
REGLINUX_MISTER_BRIDGE_POST_INSTALL_TARGET_HOOKS += REGLINUX_MISTER_BRIDGE_INSTALL_INIT

$(eval $(rust-package))
