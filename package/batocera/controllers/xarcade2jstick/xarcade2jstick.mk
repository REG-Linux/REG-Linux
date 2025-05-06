################################################################################
#
# xarcade2jstick
#
################################################################################
XARCADE2JSTICK_VERSION = 7b579e9e9554e6d997978d069ddeb566ff381007
XARCADE2JSTICK_SITE =  $(call github,petrockblog,xarcade2jstick,$(XARCADE2JSTICK_VERSION))
XARCADE2JSTICK_LICENSE = gpl3
XARCADE2JSTICK_DEPENDENCIES = linux


define XARCADE2JSTICK_BUILD_CMDS
    $(MAKE) $(TARGET_CONFIGURE_OPTS) -C $(@D) all
endef

define XARCADE2JSTICK_INSTALL_TARGET_CMDS
    $(INSTALL) -D -m 0755 $(@D)/src/xarcade2jstick $(TARGET_DIR)/usr/bin/xarcade2jstick

    # config
	mkdir -p $(TARGET_DIR)/usr/share/reglinux/datainit/system/configs/xarcade2jstick
	cp $(BR2_EXTERNAL_REGLINUX_PATH)/package/batocera/controllers/xarcade2jstick/config/* \
		$(TARGET_DIR)/usr/share/reglinux/datainit/system/configs/xarcade2jstick
endef

$(eval $(generic-package))
