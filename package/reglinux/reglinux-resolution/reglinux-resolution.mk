################################################################################
#
# reglinux resolution
#
################################################################################

REGLINUX_RESOLUTION_VERSION = 0.0
REGLINUX_RESOLUTION_LICENSE = GPL
REGLINUX_RESOLUTION_DEPENDENCIES = pciutils
REGLINUX_RESOLUTION_SOURCE=
REGLINUX_RESOLUTION_PATH = $(BR2_EXTERNAL_BATOCERA_PATH)/package/reglinux/reglinux-resolution/scripts

ifeq ($(BR2_PACKAGE_REGLINUX_SWAY),y)
REGLINUX_RESOLUTION_DEPENDENCIES += grim wf-recorder
endif

define REGLINUX_RESOLUTION_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/etc/reglinux
	install -m 0755 $(REGLINUX_RESOLUTION_PATH)/resolution/resolution.drm		$(TARGET_DIR)/etc/reglinux/
	install -m 0755 $(REGLINUX_RESOLUTION_PATH)/resolution/resolution.sway		$(TARGET_DIR)/etc/reglinux/
	install -m 0755 $(REGLINUX_RESOLUTION_PATH)/resolution/batocera-resolution	$(TARGET_DIR)/usr/bin/

	install -m 0755 $(REGLINUX_RESOLUTION_PATH)/recorder/recorder.drm		$(TARGET_DIR)/etc/reglinux/
	install -m 0755 $(REGLINUX_RESOLUTION_PATH)/recorder/recorder.sway		$(TARGET_DIR)/etc/reglinux/
	install -m 0755 $(REGLINUX_RESOLUTION_PATH)/recorder/batocera-recorder		$(TARGET_DIR)/usr/bin/
endef

$(eval $(generic-package))
