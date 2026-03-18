################################################################################
#
# OPENJAZZ
#
################################################################################
# Version.: Release on Feb 18, 2026
OPENJAZZ_VERSION = 20260301
OPENJAZZ_SITE =  $(call github,AlisterT,openjazz,$(OPENJAZZ_VERSION))
OPENJAZZ_DEPENDENCIES = sdl2
OPENJAZZ_LICENSE = GPLv2

OPENJAZZ_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release
OPENJAZZ_CONF_OPTS += -DBUILD_SHARED_LIBS=OFF
OPENJAZZ_CONF_OPTS += -DBUILD_STATIC_LIBS=ON
OPENJAZZ_CONF_OPTS += -DDATAPATH="/userdata/roms/openjazz"

define OPENJAZZ_INSTALL_TARGET_CMDS
	$(INSTALL) -D -m 0755 $(@D)/OpenJazz $(TARGET_DIR)/usr/bin/OpenJazz
	mkdir -p $(TARGET_DIR)/usr/share/reglinux/datainit/system/configs/
	cp $(BR2_EXTERNAL_REGLINUX_PATH)/package/ports/openjazz/openjazz.cfg $(TARGET_DIR)/usr/share/reglinux/datainit/system/configs/openjazz.cfg
endef

$(eval $(cmake-package))
