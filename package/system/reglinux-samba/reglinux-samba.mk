########################################################################
#
# REG-Linux-Samba - implementation using ksmbd/ksmbd_tools and/or samba
#
########################################################################

REGLINUX_SAMBA_VERSION = 0.7
REGLINUX_SAMBA_SOURCE =
REGLINUX_SAMBA_DEPENDENCIES =

# Install S91ksmbd service
define REGLINUX_SAMBA_INSTALL_KSMBD_INIT
	# Install S91ksmbd service
	$(INSTALL) -m 0755 -D $(BR2_EXTERNAL_REGLINUX_PATH)/package/system/reglinux-samba/S91ksmbd $(TARGET_DIR)/etc/init.d/S91ksmbd
	$(INSTALL) -m 0755 -D $(BR2_EXTERNAL_REGLINUX_PATH)/package/system/reglinux-samba/SAMBA $(TARGET_DIR)/usr/share/reglinux/services/SAMBA
endef

REGLINUX_SAMBA_DEPENDENCIES += ksmbd-tools
REGLINUX_SAMBA_POST_INSTALL_TARGET_HOOKS += REGLINUX_SAMBA_INSTALL_KSMBD_INIT

$(eval $(generic-package))
