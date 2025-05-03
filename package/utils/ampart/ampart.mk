################################################################################
#
# ampart (Amlogic eMMC Partition Tool)
#
################################################################################

AMPART_VERSION = v1.4.1
https://github.com/7Ji/ampart/
AMPART_SITE = $(call github,7Ji,ampart,$(AMPART_VERSION))
AMPART_LICENSE = GPL-3.0
AMPART_DEPENDENCIES += zlib

AMPART_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release

define AMPART_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/usr/bin
	$(INSTALL) -D $(@D)/ampart $(TARGET_DIR)/usr/bin/ampart
endef

$(eval $(cmake-package))
