################################################################################
#
# uboot files for RK3326
#
################################################################################

UBOOT_RK3326_VERSION = v0.0.1
UBOOT_RK3326_SITE = https://github.com/REG-Linux/uboot-rk3326/releases/download/$(UBOOT_RK3326_VERSION)
UBOOT_RK3326_SOURCE = uboot-rk3326.tar.gz

define UBOOT_RK3326_INSTALL_TARGET_CMDS
	cp $(@D)/* $(BINARIES_DIR)/
endef

$(eval $(generic-package))
