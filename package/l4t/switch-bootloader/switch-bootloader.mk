################################################################################
#
# switch-bootloader
#
# Boot orchestration for the Nintendo Switch
# Creates Hekate boot config, boot.scr, and update script
# Based on Lakka-LibreELEC's switch-bootloader package
#
################################################################################

SWITCH_BOOTLOADER_VERSION = 3.0
SWITCH_BOOTLOADER_SOURCE =
SWITCH_BOOTLOADER_LICENSE = GPL-2.0+
SWITCH_BOOTLOADER_DEPENDENCIES = host-switch-u-boot switch-u-boot switch-atf

SWITCH_BOOTLOADER_DISTRO = REG-Linux
SWITCH_BOOTLOADER_DISTRO_PATH = reglinux
SWITCH_BOOTLOADER_ID = REGLINUX

define SWITCH_BOOTLOADER_BUILD_CMDS
	# Create Hekate INI configuration
	cat > $(@D)/reglinux.ini <<- 'EOINI'
	[REG-Linux]
	l4t=1
	boot_prefixes=reglinux/boot/
	id=REGLINUX
	EOINI

	# Prepare boot script from template
	cp $(SWITCH_BOOTLOADER_PKGDIR)/boot.txt $(@D)/boot.txt
	$(SED) 's|@DISTRO_PATH@|reglinux|g' $(@D)/boot.txt
	$(SED) 's|@DISTRO_ID@|REGLINUX|g' $(@D)/boot.txt

	# Generate U-Boot boot script
	$(HOST_DIR)/bin/mkimage -A arm -T script -O linux -d $(@D)/boot.txt $(@D)/boot.scr
endef

define SWITCH_BOOTLOADER_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/usr/share/bootloader/boot

	$(INSTALL) -D -m 0644 $(@D)/boot.scr \
		$(TARGET_DIR)/usr/share/bootloader/boot/boot.scr
	$(INSTALL) -D -m 0644 $(@D)/reglinux.ini \
		$(TARGET_DIR)/usr/share/bootloader/boot/reglinux.ini

	# Create update.sh for bootloader updates
	cat > $(TARGET_DIR)/usr/share/bootloader/update.sh <<- 'EOUPDATE'
	#!/bin/sh
	[ -z "$${BOOT_ROOT}" ] && BOOT_ROOT="/flash"
	[ -z "$${SYSTEM_ROOT}" ] && SYSTEM_ROOT=""
	mkdir -p $${BOOT_ROOT}/reglinux/boot
	cp $${SYSTEM_ROOT}/usr/share/bootloader/boot/boot.scr $${BOOT_ROOT}/reglinux/boot/
	cp $${SYSTEM_ROOT}/usr/share/bootloader/boot/bl31.bin $${BOOT_ROOT}/reglinux/boot/
	cp $${SYSTEM_ROOT}/usr/share/bootloader/boot/bl33.bin $${BOOT_ROOT}/reglinux/boot/
	[ ! -f "$${BOOT_ROOT}/bootloader/ini/reglinux.ini" ] && \
		cp $${SYSTEM_ROOT}/usr/share/bootloader/boot/reglinux.ini \
		   $${BOOT_ROOT}/bootloader/ini/reglinux.ini
	EOUPDATE
	chmod +x $(TARGET_DIR)/usr/share/bootloader/update.sh
endef

$(eval $(generic-package))
