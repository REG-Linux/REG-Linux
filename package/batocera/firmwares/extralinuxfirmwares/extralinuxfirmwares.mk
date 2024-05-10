################################################################################
#
# extralinuxfirmware
#
################################################################################
# Version.: Commits on May 10, 2024
EXTRALINUXFIRMWARES_VERSION = e9c1d95f2d707ddd7bb0ef9e4711914de3cb60c2
EXTRALINUXFIRMWARES_SITE = $(call github,batocera-linux,extralinuxfirmwares,$(EXTRALINUXFIRMWARES_VERSION))
EXTRALINUXFIRMWARES_DEPENDENCIES = alllinuxfirmwares

EXTRALINUXFIRMWARES_TARGET_DIR=$(TARGET_DIR)/lib/firmware/

define EXTRALINUXFIRMWARES_INSTALL_TARGET_CMDS
	mkdir -p $(EXTRALINUXFIRMWARES_TARGET_DIR)
	cp -a $(@D)/* $(EXTRALINUXFIRMWARES_TARGET_DIR)/
endef

$(eval $(generic-package))
