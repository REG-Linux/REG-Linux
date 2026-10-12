################################################################################
#
# rtl8733bu
#
################################################################################
# WiFi half of the RTL8733BU WiFi/BT combo chip (Miyoo Flip).
# Version: Commits on Jun 20, 2026 (Linux 7.1 cfg80211 ops)
RTL8733BU_VERSION = 2b72111f68d4cfafa27f189761448c61a8b325c8
RTL8733BU_SITE = $(call github,Charliechen114514,rtl8733bu-linux-driver,$(RTL8733BU_VERSION))
RTL8733BU_LICENSE = GPL-2.0
RTL8733BU_LICENSE_FILES = LICENSE

# 001-006 from Zlyme (github.com/Zetarancio/zlyme package/drivers/rtl8733bu)
# 007 ports to Linux 7.2

RTL8733BU_MODULE_MAKE_OPTS = CONFIG_RTL8733BU=m

define RTL8733BU_INSTALL_MODPROBE_CONF
	$(INSTALL) -m 0644 -D $(RTL8733BU_PKGDIR)/8733bu.conf \
		$(TARGET_DIR)/etc/modprobe.d/8733bu.conf
endef
RTL8733BU_POST_INSTALL_TARGET_HOOKS += RTL8733BU_INSTALL_MODPROBE_CONF

$(eval $(kernel-module))
$(eval $(generic-package))
