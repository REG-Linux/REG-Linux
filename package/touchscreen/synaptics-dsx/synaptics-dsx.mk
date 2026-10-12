################################################################################
#
# synaptics-dsx — Synaptics DSX I2C touchscreen driver
#
################################################################################

SYNAPTICS_DSX_VERSION = 1.0
SYNAPTICS_DSX_SITE = $(SYNAPTICS_DSX_PKGDIR)/src
SYNAPTICS_DSX_SITE_METHOD = local
SYNAPTICS_DSX_LICENSE = GPL-2.0+

define SYNAPTICS_DSX_INSTALL_HEADER
	mkdir -p $(LINUX_DIR)/include/linux/input
	cp -f $(@D)/synaptics_dsx.h $(LINUX_DIR)/include/linux/input/
endef
SYNAPTICS_DSX_PRE_BUILD_HOOKS += SYNAPTICS_DSX_INSTALL_HEADER

$(eval $(kernel-module))
$(eval $(generic-package))
