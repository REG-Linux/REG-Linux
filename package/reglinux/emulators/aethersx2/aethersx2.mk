################################################################################
#
# AetherSX2
#
################################################################################

AETHERSX2_VERSION = 2119.1
AETHERSX2_SITE = https://github.com/Lime3DS/lime3ds-archive.git
AETHERSX2_SITE_METHOD = git
AETHERSX2_GIT_SUBMODULES=YES
AETHERSX2_LICENSE = GPLv2
AETHERSX2_DEPENDENCIES += reglinux-qt6
AETHERSX2_SUPPORTS_IN_SOURCE_BUILD = NO

define AETHERSX2_INSTALL_TARGET_CMDS
    mkdir -p $(TARGET_DIR)/usr/bin
    mkdir -p $(TARGET_DIR)/usr/lib
	$(INSTALL) -D $(@D)/buildroot-build/bin/Release/$(AETHERSX2_BIN) \
		$(TARGET_DIR)/usr/bin/
endef

# TODO evmapy
#define AETHERSX2_EVMAP
#	mkdir -p $(TARGET_DIR)/usr/share/evmapy
#	cp -prn $(BR2_EXTERNAL_REGLINUX_PATH)/package/reglinux/emulators/aethersx2/ps2.aethersx2.keys \
#		$(TARGET_DIR)/usr/share/evmapy
#endef

#AETHERSX2_POST_INSTALL_TARGET_HOOKS = AETHERSX2_EVMAP

$(eval $(generic-package))
