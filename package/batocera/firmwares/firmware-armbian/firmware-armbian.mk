################################################################################
#
# armbian firmware
#
################################################################################
# Version.: Commits on Mar 14, 2025
FIRMWARE_ARMBIAN_VERSION = 509fadf8bd4eabc122670ffc37f8e92dae68656e
FIRMWARE_ARMBIAN_SITE = $(call github,armbian,firmware,$(FIRMWARE_ARMBIAN_VERSION))

FIRMWARE_ARMBIAN_TARGET_DIR=$(TARGET_DIR)/lib/firmware/

ifeq ($(BR2_PACKAGE_ALLLINUXFIRMWARES),y)
FIRMWARE_ARMBIAN_DEPENDENCIES += alllinuxfirmwares
endif

ifeq ($(BR2_PACKAGE_FIRMWARE_KHADAS_VIM4),y)
FIRMWARE_ARMBIAN_DEPENDENCIES += firmware-khadas-vim4
endif

ifeq ($(BR2_PACKAGE_EXTRALINUXFIRMWARES),y)
FIRMWARE_ARMBIAN_DEPENDENCIES += extralinuxfirmwares
endif

define FIRMWARE_ARMBIAN_INSTALL_TARGET_CMDS
	mkdir -p $(FIRMWARE_ARMBIAN_TARGET_DIR)
	cp -aRf $(@D)/* $(FIRMWARE_ARMBIAN_TARGET_DIR)/
	# Make dracut happy
	chmod -R 666 $(FIRMWARE_ARMBIAN_TARGET_DIR)brcm/*
endef

$(eval $(generic-package))
