################################################################################
#
# REG-Linux-Samba - implementation using either ksmbd/ksmbd_tools or full samba
#
################################################################################

REGLINUX_SAMBA_VERSION = 0.1
REGLINUX_SAMBA_SOURCE =

REGLINUX_SAMBA_DEPENDENCIES =

# Remove S91smb service
define REGLINUX_SAMBA_REMOVE_SAMBA_INIT
	rm $(TARGET_DIR)/etc/init.d/S91smb
endef

# Install S91ksmbd service
define REGLINUX_SAMBA_INSTALL_KSMBD_INIT
	$(INSTALL) -m 0755 -D $(BR2_BATOCERA_EXTERNAL_PATH)/package/reglinux/reglinux-samba/S91ksmbd $(TARGET_DIR)/etc/init.d/S91ksmbd
endef

# We need samba4 for Wine x86, and old kernels
ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_X86_ANY)$(BR2_PACKAGE_BATOCERA_TARGET_RK3128)$(BR2_PACKAGE_BATOCERA_TARGET_A3GEN2)$(BR2_PACKAGE_BATOCERA_TARGET_S9GEN4)$(BR2_PACKAGE_BATOCERA_TARGET_RK3588),y)
REGLINUX_SAMBA_DEPENDENCIES += samba4
endif

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RK3128)$(BR2_PACKAGE_BATOCERA_TARGET_A3GEN2)$(BR2_PACKAGE_BATOCERA_TARGET_S9GEN4)$(BR2_PACKAGE_BATOCERA_TARGET_RK3588),)
REGLINUX_SAMBA_DEPENDENCIES += ksmbd-tools
endif

# X86 will run ksmbd, so remove S91smb
ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_X86_ANY),y)
REGLINUX_SAMBA_POST_INSTALL_HOOKS += REGLINUX_SAMBA_REMOVE_SAMBA_INIT
endif

# Everything but those archs will run ksmbd
ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RK3128)$(BR2_PACKAGE_BATOCERA_TARGET_A3GEN2)$(BR2_PACKAGE_BATOCERA_TARGET_S9GEN4)$(BR2_PACKAGE_BATOCERA_TARGET_RK3588),)
REGLINUX_SAMBA_POST_INSTALL_HOOKS += REGLINUX_SAMBA_INSTALL_KSMBD_INIT
endif

$(eval $(generic-package))
