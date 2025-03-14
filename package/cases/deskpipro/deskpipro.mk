################################################################################
#
# deskpi-pro
#
################################################################################

DESKPIPRO_VERSION = e4200553775bc88e93af1ced1bda8214cc87a00c
DESKPIPRO_SITE = $(call github,DeskPi-Team,deskpi,$(DESKPIPRO_VERSION))
DESKPIPRO_LICENSE = GPL-3.0+

ifeq ($(BR2_PACKAGE_LIRC_TOOLS),y)
DESKPIPRO_DEPENDENCIES += lirc-tools
endif

define DESKPIPRO_BUILD_CMDS
	$(HOST_DIR)/bin/aarch64-linux-gcc -o $(@D)/drivers/c/fanStop $(@D)/drivers/c/fanStop.c
	$(HOST_DIR)/bin/aarch64-linux-gcc -o $(@D)/drivers/c/pwmFanControl $(@D)/drivers/c/pwmControlFan.c
	$(HOST_DIR)/bin/aarch64-linux-gcc -o $(@D)/drivers/c/safecutoffpower $(@D)/drivers/c/safecutoffpower.c
endef

define DESKPIPRO_INSTALL_TARGET_CMDS
	$(INSTALL) -D -m 0755 $(@D)/drivers/c/fanStop $(TARGET_DIR)/usr/bin/
	$(INSTALL) -D -m 0755 $(@D)/drivers/c/pwmFanControl $(TARGET_DIR)/usr/bin/
	$(INSTALL) -D -m 0755 $(@D)/drivers/c/safecutoffpower $(TARGET_DIR)/usr/bin/
endef

$(eval $(generic-package))
