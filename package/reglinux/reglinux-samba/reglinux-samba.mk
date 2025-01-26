################################################################################
#
# REG-Linux-Samba - implementation using either ksmbd/ksmbd_tools or full samba
#
################################################################################

REGLINUX_SAMBA_VERSION = 0.5
REGLINUX_SAMBA_SOURCE =
REGLINUX_SAMBA_DEPENDENCIES =

# Install S91ksmbd service
define REGLINUX_SAMBA_INSTALL_KSMBD_INIT
	# Install S91ksmbd service
	$(INSTALL) -m 0755 -D $(BR2_EXTERNAL_REGLINUX_PATH)/package/reglinux/reglinux-samba/S91ksmbd $(TARGET_DIR)/etc/init.d/S91smbd
endef

# Install S91smbd service
define REGLINUX_SAMBA_INSTALL_SMBD_INIT
	# Install S91smbd service
	$(INSTALL) -m 0755 -D $(BR2_EXTERNAL_REGLINUX_PATH)/package/reglinux/reglinux-samba/S91smbd $(TARGET_DIR)/etc/init.d/S91smbd
endef

# We need samba4 for Wine
ifeq ($(BR2_PACKAGE_BATOCERA_WINE),y)
REGLINUX_SAMBA_DEPENDENCIES += samba4
endif

# We use samba4 as SMB service for old kernels (< 5.15), if not you run ksmbd
ifeq ($(BR2_PACKAGE_HOST_LINUX_HEADERS_CUSTOM_5_4),y)
REGLINUX_SAMBA_DEPENDENCIES += samba4
REGLINUX_SAMBA_POST_INSTALL_TARGET_HOOKS += REGLINUX_SAMBA_INSTALL_SMBD_INIT
else
REGLINUX_SAMBA_DEPENDENCIES += ksmbd-tools
REGLINUX_SAMBA_POST_INSTALL_TARGET_HOOKS += REGLINUX_SAMBA_INSTALL_KSMBD_INIT
endif

$(eval $(generic-package))
