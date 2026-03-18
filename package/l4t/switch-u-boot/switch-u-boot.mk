################################################################################
#
# switch-u-boot
#
# CTCaer's modified U-Boot for the Nintendo Switch (Tegra T210)
# Based on Lakka-LibreELEC's switch-u-boot package
#
################################################################################

SWITCH_U_BOOT_VERSION = 2606ef5dfa14faedca16f2dcdea59719c7c963f7
SWITCH_U_BOOT_SITE = https://github.com/CTCaer/switch-l4t-uboot.git
SWITCH_U_BOOT_SITE_METHOD = git
SWITCH_U_BOOT_GIT_SUBMODULES = YES
SWITCH_U_BOOT_LICENSE = GPL-2.0+
SWITCH_U_BOOT_LICENSE_FILES = Licenses/gpl-2.0.txt
SWITCH_U_BOOT_DEPENDENCIES = host-switch-u-boot host-python3 host-swig host-bison host-flex

# Host build: produces mkimage tool
HOST_SWITCH_U_BOOT_DEPENDENCIES = host-python3 host-swig host-bison host-flex

define HOST_SWITCH_U_BOOT_BUILD_CMDS
	$(HOST_MAKE_ENV) $(MAKE) -C $(@D) \
		ARCH=arm64 CROSS_COMPILE="$(TARGET_CROSS)" \
		nintendo-switch_defconfig
	$(HOST_MAKE_ENV) $(MAKE) -C $(@D) tools-only
endef

define HOST_SWITCH_U_BOOT_INSTALL_CMDS
	$(INSTALL) -D -m 0755 $(@D)/tools/mkimage $(HOST_DIR)/bin/mkimage
endef

# Target build: produces bl33.bin (U-Boot binary)
define SWITCH_U_BOOT_BUILD_CMDS
	$(TARGET_MAKE_ENV) $(MAKE) -C $(@D) \
		ARCH=arm64 CROSS_COMPILE="$(TARGET_CROSS)" \
		nintendo-switch_defconfig
	$(TARGET_MAKE_ENV) $(MAKE) -C $(@D) \
		ARCH=arm64 CROSS_COMPILE="$(TARGET_CROSS)"
endef

define SWITCH_U_BOOT_INSTALL_TARGET_CMDS
	$(INSTALL) -D -m 0644 $(@D)/u-boot-dtb.bin \
		$(TARGET_DIR)/usr/share/bootloader/boot/bl33.bin
endef

$(eval $(generic-package))
$(eval $(host-generic-package))
