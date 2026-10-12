################################################################################
#
# reglinux-triggerhappy
#
################################################################################

REGLINUX_TRIGGERHAPPY_VERSION = 1.0
REGLINUX_TRIGGERHAPPY_DEPENDENCIES = triggerhappy
REGLINUX_TRIGGERHAPPY_SOURCE=

define REGLINUX_TRIGGERHAPPY_INSTALL_CONFIG
	rm -rf $(TARGET_DIR)/etc/init.d/S*triggerhappy
	$(INSTALL) -Dm644 $(REGLINUX_TRIGGERHAPPY_PKGDIR)/conf/multimedia_keys.conf          $(TARGET_DIR)/etc/triggerhappy/triggers.d/multimedia_keys.conf
	$(INSTALL) -Dm644 $(REGLINUX_TRIGGERHAPPY_PKGDIR)/conf/multimedia_keys_disabled.conf $(TARGET_DIR)/etc/triggerhappy/triggers.d/multimedia_keys_disabled.conf
	$(INSTALL) -Dm755 $(REGLINUX_TRIGGERHAPPY_PKGDIR)/S50triggerhappy                    $(TARGET_DIR)/etc/init.d/S50triggerhappy
endef

define REGLINUX_TRIGGERHAPPY_INSTALL_RK3326_CONFIG
    cp -v $(REGLINUX_TRIGGERHAPPY_PKGDIR)/conf/rk3326/*.conf $(TARGET_DIR)/etc/triggerhappy/triggers.d/
endef

define REGLINUX_TRIGGERHAPPY_INSTALL_RK3568_CONFIG
	cp -v $(REGLINUX_TRIGGERHAPPY_PKGDIR)/conf/rk3568/*.conf $(TARGET_DIR)/etc/triggerhappy/triggers.d/
endef

define REGLINUX_TRIGGERHAPPY_INSTALL_X86_64_CONFIG
	cp -v $(REGLINUX_TRIGGERHAPPY_PKGDIR)/conf/x86_64/*.conf $(TARGET_DIR)/etc/triggerhappy/triggers.d/
endef

REGLINUX_TRIGGERHAPPY_POST_INSTALL_TARGET_HOOKS += REGLINUX_TRIGGERHAPPY_INSTALL_CONFIG

ifeq ($(BR2_PACKAGE_SYSTEM_TARGET_RK3326),y)
	REGLINUX_TRIGGERHAPPY_POST_INSTALL_TARGET_HOOKS += REGLINUX_TRIGGERHAPPY_INSTALL_RK3326_CONFIG
endif

ifeq ($(BR2_PACKAGE_SYSTEM_TARGET_RK3568),y)
	REGLINUX_TRIGGERHAPPY_POST_INSTALL_TARGET_HOOKS += REGLINUX_TRIGGERHAPPY_INSTALL_RK3568_CONFIG
endif

ifeq ($(BR2_PACKAGE_SYSTEM_TARGET_X86_64_ANY),y)
	REGLINUX_TRIGGERHAPPY_POST_INSTALL_TARGET_HOOKS += REGLINUX_TRIGGERHAPPY_INSTALL_X86_64_CONFIG
endif

$(eval $(generic-package))
