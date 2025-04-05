################################################################################
#
# inputplumber
#
################################################################################

INPUTPLUMBER_VERSION = v0.51.0
INPUTPLUMBER_SOURCE = foo-$(INPUTPLUMBER_VERSION).tar.gz
INPUTPLUMBER_SITE = $(call github,ShadowBlip,InputPlumber,$(INPUTPLUMBER_VERSION))
INPUTPLUMBER_LICENSE = GPLv3
INPUTPLUMBER_LICENSE_FILES = LICENSE

INPUTPLUMBER_DEPENDENCIES = host-clang libevdev libiio udev

INPUTPLUMBER_CARGO_INSTALL_OPTS = --path ./

$(eval $(rust-package))
