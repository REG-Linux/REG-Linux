################################################################################
#
# armbian firmware
#
################################################################################
# Version.: Commits on May 27, 2025
FIRMWARE_ARMBIAN_VERSION = 50bdc752ac908ff60fb681143a66b2561237f262
FIRMWARE_ARMBIAN_SITE = $(call github,armbian,firmware,$(FIRMWARE_ARMBIAN_VERSION))

FIRMWARE_ARMBIAN_TARGET_DIR=$(TARGET_DIR)/lib/firmware/

ifeq ($(BR2_PACKAGE_ALLLINUXFIRMWARES),y)
FIRMWARE_ARMBIAN_DEPENDENCIES += alllinuxfirmwares
endif

ifeq ($(BR2_PACKAGE_FIRMWARE_KHADAS_VIM4),y)
FIRMWARE_ARMBIAN_DEPENDENCIES += firmware-khadas-vim4
endif

define FIRMWARE_ARMBIAN_INSTALL_TARGET_CMDS
	mkdir -p $(FIRMWARE_ARMBIAN_TARGET_DIR)
	cp -aRf $(@D)/* $(FIRMWARE_ARMBIAN_TARGET_DIR)/
	# Make dracut happy
	chmod -R 666 $(FIRMWARE_ARMBIAN_TARGET_DIR)brcm/*
endef

$(eval $(generic-package))
