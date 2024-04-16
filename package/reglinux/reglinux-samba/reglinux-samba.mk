################################################################################
#
# REG-Linux-Samba - implementation using either ksmbd/libsmbclient or full samba
#
################################################################################

REGLINUX_SAMBA_VERSION = 0.1
REGLINUX_SAMBA_SOURCE =

# Those archs use too old kernel to have ksmbd, just use full samba4 for now
ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RK3128)$(BR2_PACKAGE_BATOCERA_TARGET_A3GEN2)$(BR2_PACKAGE_BATOCERA_TARGET_S9GEN4)$(BR2_PACKAGE_BATOCERA_TARGET_RK3588),y)
REGLINUX_SAMBA_DEPENDENCIES = samba4
else
REGLINUX_SAMBA_DEPENDENCIES = libsmbclient ksmbd-tools
endif

$(eval $(generic-package))
