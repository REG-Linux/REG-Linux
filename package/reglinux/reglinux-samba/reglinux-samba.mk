################################################################################
#
# REG-Linux-Samba - implementation using either ksmbd/ksmbd_tools or full samba
#
################################################################################

REGLINUX_SAMBA_VERSION = 0.1
REGLINUX_SAMBA_SOURCE =

REGLINUX_SAMBA_DEPENDENCIES =


# Install S91ksmbd service
define REGLINUX_SAMBA_INSTALL_KSMBD_INIT
	# Remove S91smb service
	if test -f "$(TARGET_DIR)/etc/init.d/S91smb"; then rm $(TARGET_DIR)/etc/init.d/S91smb ; fi
	# Install S91ksmbd instead
	$(INSTALL) -m 0755 -D $(BR2_EXTERNAL_BATOCERA_PATH)/package/reglinux/reglinux-samba/S91ksmbd $(TARGET_DIR)/etc/init.d/S91ksmbd
endef

# We need samba4 for Wine x86, and old kernels
ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_X86_ANY)$(BR2_PACKAGE_HOST_LINUX_HEADERS_CUSTOM_4_4)$(BR2_PACKAGE_HOST_LINUX_HEADERS_CUSTOM_5_4)$(BR2_PACKAGE_HOST_LINUX_HEADERS_CUSTOM_5_10),y)
REGLINUX_SAMBA_DEPENDENCIES += samba4
endif

# Everything but those archs will run ksmbd
ifneq ($(BR2_PACKAGE_BATOCERA_TARGET_RK3128)$(BR2_PACKAGE_BATOCERA_TARGET_A3GEN2)$(BR2_PACKAGE_BATOCERA_TARGET_S9GEN4)$(BR2_PACKAGE_BATOCERA_TARGET_RK3588),y)
REGLINUX_SAMBA_DEPENDENCIES += ksmbd-tools
REGLINUX_SAMBA_POST_INSTALL_TARGET_HOOKS += REGLINUX_SAMBA_INSTALL_KSMBD_INIT
endif

$(eval $(generic-package))
