################################################################################
#
# inputplumber
#
################################################################################

INPUTPLUMBER_VERSION = v0.52.1
INPUTPLUMBER_SOURCE = foo-$(INPUTPLUMBER_VERSION).tar.gz
INPUTPLUMBER_SITE = $(call github,ShadowBlip,InputPlumber,$(INPUTPLUMBER_VERSION))
INPUTPLUMBER_LICENSE = GPLv3
INPUTPLUMBER_LICENSE_FILES = LICENSE

INPUTPLUMBER_DEPENDENCIES = host-clang libevdev libiio udev

INPUTPLUMBER_CARGO_INSTALL_OPTS = --path ./

define INPUTPLUMBER_INSTALL_CONFIGS
	mkdir -p $(TARGET_DIR)/usr/share/inputplumber
	rsync -arv $(@D)/rootfs/usr/share/inputplumber/ $(TARGET_DIR)/usr/share/inputplumber/
endef

INPUTPLUMBER_POST_INSTALL_TARGET_HOOKS += INPUTPLUMBER_INSTALL_CONFIGS

$(eval $(rust-package))
