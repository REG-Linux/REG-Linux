################################################################################
#
# batocera scripts
#
################################################################################

REGLINUX_SCRIPTS_VERSION = 3
REGLINUX_SCRIPTS_LICENSE = GPL
REGLINUX_SCRIPTS_DEPENDENCIES = pciutils
REGLINUX_SCRIPTS_SOURCE=

REGLINUX_SCRIPTS_PATH = $(BR2_EXTERNAL_REGLINUX_PATH)/package/system/reglinux-scripts

# mouse type #
ifeq ($(BR2_PACKAGE_REGLINUX_XWAYLAND),y)
  REGLINUX_SCRIPTS_MOUSE_TYPE=xorg
  REGLINUX_SCRIPTS_POST_INSTALL_TARGET_HOOKS += REGLINUX_SCRIPTS_INSTALL_MOUSE
endif

ifeq ($(BR2_PACKAGE_REGLINUX_SWAY),y)
  REGLINUX_SCRIPTS_MOUSE_TYPE=wayland-sway
  REGLINUX_SCRIPTS_POST_INSTALL_TARGET_HOOKS += REGLINUX_SCRIPTS_INSTALL_MOUSE
endif
###

ifeq ($(BR2_PACKAGE_SYSTEM_TARGET_SM6115)$(BR2_PACKAGE_SYSTEM_TARGET_SM8250)$(BR2_PACKAGE_SYSTEM_TARGET_SM8550),y)
  REGLINUX_SCRIPTS_POST_INSTALL_TARGET_HOOKS += REGLINUX_SCRIPTS_INSTALL_QCOM
endif

define REGLINUX_SCRIPTS_INSTALL_TARGET_CMDS
    mkdir -p $(TARGET_DIR)/usr/lib/python$(PYTHON3_VERSION_MAJOR)
    mkdir -p $(TARGET_DIR)/usr/bin
    install -m 0755 $(REGLINUX_SCRIPTS_PATH)/scripts/bluetooth/bluezutils.py            $(TARGET_DIR)/usr/lib/python$(PYTHON3_VERSION_MAJOR)/ # any variable ?
    install -m 0755 $(REGLINUX_SCRIPTS_PATH)/scripts/bluetooth/system-bluetooth         $(TARGET_DIR)/usr/bin/
    install -m 0755 $(REGLINUX_SCRIPTS_PATH)/scripts/bluetooth/system-bluetooth-agent   $(TARGET_DIR)/usr/bin/
    install -m 0755 $(REGLINUX_SCRIPTS_PATH)/scripts/system-save-overlay                $(TARGET_DIR)/usr/bin/
    install -m 0755 $(REGLINUX_SCRIPTS_PATH)/scripts/system-usbmount                    $(TARGET_DIR)/usr/bin/
    install -m 0755 $(REGLINUX_SCRIPTS_PATH)/scripts/system-encode                      $(TARGET_DIR)/usr/bin/
    install -m 0755 $(REGLINUX_SCRIPTS_PATH)/scripts/system-padsinfo                    $(TARGET_DIR)/usr/bin/
    install -m 0755 $(REGLINUX_SCRIPTS_PATH)/scripts/system-info                        $(TARGET_DIR)/usr/bin/
    install -m 0755 $(REGLINUX_SCRIPTS_PATH)/scripts/system-install                     $(TARGET_DIR)/usr/bin/
    install -m 0755 $(REGLINUX_SCRIPTS_PATH)/scripts/system-format                      $(TARGET_DIR)/usr/bin/
    install -m 0755 $(REGLINUX_SCRIPTS_PATH)/scripts/system-mount                       $(TARGET_DIR)/usr/bin/
    install -m 0755 $(REGLINUX_SCRIPTS_PATH)/scripts/system-overclock                   $(TARGET_DIR)/usr/bin/
    install -m 0755 $(REGLINUX_SCRIPTS_PATH)/scripts/system-part                        $(TARGET_DIR)/usr/bin/
    install -m 0755 $(REGLINUX_SCRIPTS_PATH)/scripts/system-support                     $(TARGET_DIR)/usr/bin/
    install -m 0755 $(REGLINUX_SCRIPTS_PATH)/scripts/system-version                     $(TARGET_DIR)/usr/bin/
    install -m 0755 $(REGLINUX_SCRIPTS_PATH)/scripts/system-sync                        $(TARGET_DIR)/usr/bin/
    install -m 0755 $(REGLINUX_SCRIPTS_PATH)/scripts/system-upgrade                     $(TARGET_DIR)/usr/bin/
    install -m 0755 $(REGLINUX_SCRIPTS_PATH)/scripts/system-systems                     $(TARGET_DIR)/usr/bin/
    install -m 0755 $(REGLINUX_SCRIPTS_PATH)/scripts/system-config                      $(TARGET_DIR)/usr/bin/
    install -m 0755 $(REGLINUX_SCRIPTS_PATH)/scripts/system-es-thebezelproject          $(TARGET_DIR)/usr/bin/
    install -m 0755 $(REGLINUX_SCRIPTS_PATH)/scripts/system-cores                       $(TARGET_DIR)/usr/bin/
    install -m 0755 $(REGLINUX_SCRIPTS_PATH)/scripts/system-wifi                        $(TARGET_DIR)/usr/bin/
    install -m 0755 $(REGLINUX_SCRIPTS_PATH)/scripts/system-brightness                  $(TARGET_DIR)/usr/bin/
    install -m 0755 $(REGLINUX_SCRIPTS_PATH)/scripts/system-es-swissknife               $(TARGET_DIR)/usr/bin/
    install -m 0755 $(REGLINUX_SCRIPTS_PATH)/scripts/system-store                       $(TARGET_DIR)/usr/bin/
    install -m 0755 $(REGLINUX_SCRIPTS_PATH)/scripts/system-autologin                   $(TARGET_DIR)/usr/bin/
    install -m 0755 $(REGLINUX_SCRIPTS_PATH)/scripts/system-timezone                    $(TARGET_DIR)/usr/bin/
    install -m 0755 $(REGLINUX_SCRIPTS_PATH)/scripts/system-gameforce                   $(TARGET_DIR)/usr/bin/
    install -m 0755 $(REGLINUX_SCRIPTS_PATH)/scripts/system-shutdown                    $(TARGET_DIR)/usr/bin/
    install -m 0755 $(REGLINUX_SCRIPTS_PATH)/scripts/system-services                    $(TARGET_DIR)/usr/bin/
    install -m 0755 $(REGLINUX_SCRIPTS_PATH)/scripts/system-planemode                   $(TARGET_DIR)/usr/bin/
    install -m 0755 $(REGLINUX_SCRIPTS_PATH)/scripts/system-switch-screen-checker       $(TARGET_DIR)/usr/bin/
    install -m 0755 $(REGLINUX_SCRIPTS_PATH)/scripts/system-switch-screen-checker-delayed     $(TARGET_DIR)/usr/bin/
    install -m 0755 $(REGLINUX_SCRIPTS_PATH)/scripts/system-ikemen                      $(TARGET_DIR)/usr/bin/
    install -m 0644 $(REGLINUX_SCRIPTS_PATH)/rules/80-switch-screen.rules               $(TARGET_DIR)/etc/udev/rules.d
    mkdir -p $(TARGET_DIR)/etc/udev/rules.d
    install -m 0755 $(REGLINUX_SCRIPTS_PATH)/scripts/system-amd-tdp                     $(TARGET_DIR)/usr/bin/
    install -m 0755 $(REGLINUX_SCRIPTS_PATH)/scripts/system-get-nvidia-list             $(TARGET_DIR)/usr/bin/
    install -m 0755 $(REGLINUX_SCRIPTS_PATH)/scripts/system-led-effects                 $(TARGET_DIR)/usr/bin/
    install -m 0755 $(REGLINUX_SCRIPTS_PATH)/scripts/system-spinner-calibrator          $(TARGET_DIR)/usr/bin/
    install -m 0755 $(REGLINUX_SCRIPTS_PATH)/scripts/system-vulkan                      $(TARGET_DIR)/usr/bin/
    install -m 0755 $(REGLINUX_SCRIPTS_PATH)/scripts/system-power-mode                  $(TARGET_DIR)/usr/bin/
endef

define REGLINUX_SCRIPTS_INSTALL_MOUSE
    install -m 0755 $(REGLINUX_SCRIPTS_PATH)/scripts/system-mouse.${REGLINUX_SCRIPTS_MOUSE_TYPE} $(TARGET_DIR)/usr/bin/system-mouse
endef

define REGLINUX_SCRIPTS_INSTALL_ROCKCHIP
    mkdir -p $(TARGET_DIR)/usr/bin/
    install -m 0755 $(REGLINUX_SCRIPTS_PATH)/scripts/system-rockchip-suspend $(TARGET_DIR)/usr/bin/
endef

define REGLINUX_SCRIPTS_INSTALL_QCOM
    install -m 0755 $(REGLINUX_SCRIPTS_PATH)/scripts/qcom-fan $(TARGET_DIR)/usr/bin/
endef

$(eval $(generic-package))
