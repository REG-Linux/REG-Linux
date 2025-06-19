################################################################################
#
# firmware-orangepi
#
################################################################################
# Version.: Commits on Mar 19, 2025
FIRMWARE_ORANGEPI_VERSION = db5e86200ae592c467c4cfa50ec0c66cbc40b158
FIRMWARE_ORANGEPI_SITE = $(call github,orangepi-xunlong,firmware,$(FIRMWARE_ORANGEPI_VERSION))

FIRMWARE_ORANGEPI_TARGET_DIR=$(TARGET_DIR)/lib/firmware/

define FIRMWARE_ORANGEPI_INSTALL_TARGET_CMDS
	mkdir -p $(FIRMWARE_ORANGEPI_TARGET_DIR)
	cp -a $(@D)/* $(FIRMWARE_ORANGEPI_TARGET_DIR)/
endef

$(eval $(generic-package))
