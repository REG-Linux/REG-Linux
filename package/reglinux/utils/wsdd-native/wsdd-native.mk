################################################################################
#
# wsdd-native
#
################################################################################

WSDD_NATIVE_VERSION = 1.14
WSDD_NATIVE_SITE = $(call github,gershnik,wsdd-native,v$(WSDD_NATIVE_VERSION))
WSDD_NATIVE_LICENSE = BSD

WSDD_NATIVE_DEPENDENCIES += host-cmake host-libxml2 libxml2
WSDD_NATIVE_CONF_OPTS += -DWSDDN_PREFER_SYSTEM=ON -DWSDDN_WITH_SYSTEMD="no" -DCMAKE_BUILD_TYPE=Release

define WSDD_NATIVE_INSTALL_TARGET_CMDS
        $(INSTALL) -Dm755 $(@D)/wsddn $(TARGET_DIR)/usr/bin/wsdd
        $(INSTALL) -Dm755 $(BR2_EXTERNAL_BATOCERA_PATH)/package/reglinux/utils/wsdd-native/S93wsdd $(TARGET_DIR)/etc/init.d
endef

$(eval $(cmake-package))
