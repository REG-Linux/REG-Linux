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

ifeq ($(BR2_PACKAGE_REGLINUX_LLVM_BUILD_FROM_SOURCE),y)
INPUTPLUMBER_DEPENDENCIES = host-clang libevdev libiio udev
else
INPUTPLUMBER_DEPENDENCIES = reglinux-llvm libevdev libiio udev
endif

INPUTPLUMBER_CARGO_INSTALL_OPTS = --path ./

define INPUTPLUMBER_INSTALL_CONFIGS
	mkdir -p $(TARGET_DIR)/usr/share/inputplumber
	rsync -arv $(@D)/rootfs/usr/share/inputplumber/ $(TARGET_DIR)/usr/share/inputplumber/
endef

INPUTPLUMBER_POST_INSTALL_TARGET_HOOKS += INPUTPLUMBER_INSTALL_CONFIGS

$(eval $(rust-package))
