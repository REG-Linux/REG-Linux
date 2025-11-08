################################################################################
#
# armbian firmware
#
################################################################################
# Version.: Commits on Nov 5, 2025
FIRMWARE_ARMBIAN_VERSION = 5d4dd2fc8dd4e28ac4c85696b8ab86775babc7c7
FIRMWARE_ARMBIAN_SITE = $(call github,armbian,firmware,$(FIRMWARE_ARMBIAN_VERSION))

FIRMWARE_ARMBIAN_TARGET_DIR=$(TARGET_DIR)/lib/firmware/

ifeq ($(BR2_PACKAGE_ALLLINUXFIRMWARES),y)
FIRMWARE_ARMBIAN_DEPENDENCIES += alllinuxfirmwares
endif

# Remove qualcomm firmware if not building for snapdragon targets
ifneq ($(BR2_PACKAGE_SYSTEM_TARGET_ODIN)$(BR2_PACKAGE_SYSTEM_TARGET_SM6115)$(BR2_PACKAGE_SYSTEM_TARGET_SM8250)$(BR2_PACKAGE_SYSTEM_TARGET_SM8550),y)
    FIRMWARE_ARMBIAN_REMOVE_FILES += $(@D)/qcom
endif

define FIRMWARE_ARMBIAN_INSTALL_TARGET_CMDS
	# exclude some dirs not required on REG
	rm -rf $(FIRMWARE_ARMBIAN_REMOVE_FILES)

	# Copy data
	mkdir -p $(FIRMWARE_ARMBIAN_TARGET_DIR)
	cp -aRf $(@D)/* $(FIRMWARE_ARMBIAN_TARGET_DIR)/

	# Make dracut happy
	chmod -R 666 $(FIRMWARE_ARMBIAN_TARGET_DIR)brcm/*
endef

$(eval $(generic-package))
