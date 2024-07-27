################################################################################
#
# OPENJAZZ
#
################################################################################
# Version.: Commits on Apr 15, 2024
OPENJAZZ_VERSION = 1e1adcd815bd79854b9787bc542fec6ad84f23e2
OPENJAZZ_SITE =  $(call github,AlisterT,openjazz,$(OPENJAZZ_VERSION))
OPENJAZZ_DEPENDENCIES = sdl2
OPENJAZZ_LICENSE = GPLv2

define OPENJAZZ_INSTALL_TARGET_CMDS
	$(INSTALL) -D -m 0755 $(@D)/OpenJazz $(TARGET_DIR)/usr/bin/OpenJazz
endef

define OPENJAZZ_POST_PROCESS
	mkdir -p $(TARGET_DIR)/usr/share/evmapy
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/reglinux/ports/openjazz/openjazz.keys $(TARGET_DIR)/usr/share/evmapy
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/reglinux/ports/openjazz/openjazz.cfg $(TARGET_DIR)/usr/share/batocera/datainit/system/configs/openjazz.cfg
endef

$(eval $(cmake-package))

