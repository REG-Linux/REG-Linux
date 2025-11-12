################################################################################
#
# system-settings:
# keep backward compatibility while scripts are converted to use regmsg
#
################################################################################

REGLINUX_SYSTEM_SETTINGS_VERSION = 1
REGLINUX_SYSTEM_SETTINGS_SOURCE =

define REGLINUX_SYSTEM_SETTINGS_INSTALL_TARGET_CMDS
    rm -fv $(TARGET_DIR)/usr/bin/system-settings*
    $(INSTALL) -m 0755 -D $(BR2_EXTERNAL_REGLINUX_PATH)/package/system/reglinux-system-settings/system-settings-get $(TARGET_DIR)/usr/bin/system-settings-get
    ln -s /usr/bin/system-settings-get $(TARGET_DIR)/usr/bin/system-settings-get-master
    $(INSTALL) -m 0755 -D $(BR2_EXTERNAL_REGLINUX_PATH)/package/system/reglinux-system-settings/system-settings-set $(TARGET_DIR)/usr/bin/system-settings-set
endef

$(eval $(generic-package))
