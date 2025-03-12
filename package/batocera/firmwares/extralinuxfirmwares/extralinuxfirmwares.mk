################################################################################
#
# extralinuxfirmware
#
################################################################################
# Version.: Commits on Mar 11, 2025
EXTRALINUXFIRMWARES_VERSION = 96480509110b50313203bdee11385a1de27fb514
EXTRALINUXFIRMWARES_SITE = $(call github,REG-Linux,extralinuxfirmwares,$(EXTRALINUXFIRMWARES_VERSION))
EXTRALINUXFIRMWARES_DEPENDENCIES = alllinuxfirmwares

EXTRALINUXFIRMWARES_TARGET_DIR=$(TARGET_DIR)/lib/firmware/

define EXTRALINUXFIRMWARES_INSTALL_TARGET_CMDS
	mkdir -p $(EXTRALINUXFIRMWARES_TARGET_DIR)
	cp -a $(@D)/* $(EXTRALINUXFIRMWARES_TARGET_DIR)/
endef

$(eval $(generic-package))
