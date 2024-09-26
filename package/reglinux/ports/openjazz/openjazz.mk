################################################################################
#
# OPENJAZZ
#
################################################################################
# Version.: Release on Sep 19, 2024
OPENJAZZ_VERSION = 20240919
OPENJAZZ_SITE =  $(call github,AlisterT,openjazz,$(OPENJAZZ_VERSION))
OPENJAZZ_DEPENDENCIES = sdl2
OPENJAZZ_LICENSE = GPLv2

define OPENJAZZ_INSTALL_TARGET_CMDS
	$(INSTALL) -D -m 0755 $(@D)/OpenJazz $(TARGET_DIR)/usr/bin/OpenJazz
endef

define OPENJAZZ_POST_PROCESS
	mkdir -p $(TARGET_DIR)/usr/share/evmapy
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/reglinux/ports/openjazz/openjazz.keys $(TARGET_DIR)/usr/share/evmapy
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/reglinux/ports/openjazz/openjazz.cfg $(TARGET_DIR)/usr/share/reglinux/datainit/system/configs/openjazz.cfg
endef

$(eval $(cmake-package))

