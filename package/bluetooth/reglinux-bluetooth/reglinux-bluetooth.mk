################################################################################
#
# reglinux-bluetooth
#
################################################################################

REGLINUX_BLUETOOTH_VERSION = 2.2
REGLINUX_BLUETOOTH_LICENSE = GPL
REGLINUX_BLUETOOTH_SOURCE=

REGLINUX_BLUETOOTH_STACK=

ifeq ($(BR2_PACKAGE_SYSTEM_TARGET_RPI_GLES2),y) # all but RPi4
	REGLINUX_BLUETOOTH_STACK=bcm921 piscan
else ifeq ($(BR2_PACKAGE_SYSTEM_TARGET_RK3288),y) # tinkerboard only ??
	REGLINUX_BLUETOOTH_STACK=rfkreset rtk115
else ifeq ($(BR2_PACKAGE_SYSTEM_TARGET_RK3399),y)
	REGLINUX_BLUETOOTH_STACK=rfkreset bcm150
else ifeq ($(BR2_PACKAGE_SYSTEM_TARGET_SUN50I)$(BR2_PACKAGE_SYSTEM_TARGET_H616)$(BR2_PACKAGE_SYSTEM_TARGET_H700),y)
	REGLINUX_BLUETOOTH_STACK=rfkreset sprd
else ifeq ($(BR2_PACKAGE_SYSTEM_TARGET_S9GEN4),y)
	REGLINUX_BLUETOOTH_STACK=kvim1s
else ifeq ($(BR2_PACKAGE_SYSTEM_TARGET_A3GEN2),y)
	REGLINUX_BLUETOOTH_STACK=kvim4
else ifeq ($(BR2_PACKAGE_SYSTEM_TARGET_K1),y)
	REGLINUX_BLUETOOTH_STACK=k1bt
endif

define REGLINUX_BLUETOOTH_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/etc/init.d/
	mkdir -p $(TARGET_DIR)/etc/dbus-1/system.d
	cp $(BR2_EXTERNAL_REGLINUX_PATH)/package/bluetooth/reglinux-bluetooth/S30bluetooth.template \
		$(TARGET_DIR)/etc/init.d/S30bluetooth
	cp $(BR2_EXTERNAL_REGLINUX_PATH)/package/bluetooth/reglinux-bluetooth/bluetooth.conf \
		$(TARGET_DIR)/etc/dbus-1/system.d/bluetooth.conf
	sed -i -e s+"@INTERNAL_BLUETOOTH_STACK@"+"$(REGLINUX_BLUETOOTH_STACK)"+ \
		$(TARGET_DIR)/etc/init.d/S30bluetooth
endef

$(eval $(generic-package))
