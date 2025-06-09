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

ifeq ($(BR2_PACKAGE_EXTRALINUXFIRMWARES),y)
FIRMWARE_ARMBIAN_DEPENDENCIES += extralinuxfirmwares
endif

define FIRMWARE_ARMBIAN_INSTALL_TARGET_CMDS
	mkdir -p $(FIRMWARE_ARMBIAN_TARGET_DIR)
	# Remove dangling symlinks before copying
	find $(FIRMWARE_ARMBIAN_TARGET_DIR) -type l ! -exec test -e {} \; -delete
	cp -aRf $(@D)/* $(FIRMWARE_ARMBIAN_TARGET_DIR)/
	# Make dracut happy (only if directory exists)
	if [ -d "$(FIRMWARE_ARMBIAN_TARGET_DIR)/brcm" ]; then \
	    chmod -R 666 $(FIRMWARE_ARMBIAN_TARGET_DIR)/brcm/*; \
	fi
endef

$(eval $(generic-package))
