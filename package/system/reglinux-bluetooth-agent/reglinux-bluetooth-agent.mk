################################################################################
#
# reglinux-bluetooth-agent
#
################################################################################

REGLINUX_BLUETOOTH_AGENT_VERSION = 1.0
REGLINUX_BLUETOOTH_AGENT_LICENSE = GPL-2.0+
REGLINUX_BLUETOOTH_AGENT_DEPENDENCIES = basu
REGLINUX_BLUETOOTH_AGENT_SOURCE =

define REGLINUX_BLUETOOTH_AGENT_BUILD_CMDS
	$(TARGET_CC) $(TARGET_CFLAGS) \
		-o $(@D)/system-bluetooth-agent \
		$(BR2_EXTERNAL_REGLINUX_PATH)/package/system/reglinux-bluetooth-agent/src/main.c \
		-lbasu
endef

define REGLINUX_BLUETOOTH_AGENT_INSTALL_TARGET_CMDS
	install -m 0755 $(@D)/system-bluetooth-agent $(TARGET_DIR)/usr/bin/system-bluetooth-agent
endef

$(eval $(generic-package))
