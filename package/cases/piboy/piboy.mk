################################################################################
#
# PIBOY
#
################################################################################
# Version.: Commits on Nov 1, 2021
PIBOY_VERSION = a93fe087307d676381c196ba8f098d07190cfcb0
PIBOY_SITE = $(call github,hancock33,piboycontrols,$(PIBOY_VERSION))
PIBOY_DEPENDENCIES = linux
BR2_EXTERNAL_PIBOY_PATH=$(BR2_EXTERNAL_REGLINUX_PATH)/package/cases/piboy

define PIBOY_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/usr/bin
	mkdir -p $(TARGET_DIR)/usr/share/piboy

	$(INSTALL) -D -m 0755 $(BR2_EXTERNAL_PIBOY_PATH)/piboy_fan_ctrl.py      $(TARGET_DIR)/usr/bin/piboy_fan_ctrl.py
	$(INSTALL) -D -m 0755 $(BR2_EXTERNAL_PIBOY_PATH)/piboy_aud_ctrl.py      $(TARGET_DIR)/usr/bin/piboy_aud_ctrl.py
	$(INSTALL) -D -m 0755 $(BR2_EXTERNAL_PIBOY_PATH)/piboy_power_ctrl.py    $(TARGET_DIR)/usr/bin/piboy_power_ctrl.py
	cp -a $(BR2_EXTERNAL_PIBOY_PATH)/fan.ini                                $(TARGET_DIR)/usr/share/piboy/fan.ini
endef

$(eval $(kernel-module))
$(eval $(generic-package))
