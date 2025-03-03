################################################################################
#
# asahi-alsa-ucm-conf
#
################################################################################

ASAHI_ALSA_UCM_CONF_VERSION = v6
ASAHI_ALSA_UCM_CONF_SITE = $(call github,AsahiLinux,/alsa-ucm-conf-asahi,$(ASAHI_ALSA_UCM_CONF_VERSION))
ASAHI_ALSA_UCM_CONF_LICENSE = BSD-3-Clause
ASAHI_ALSA_UCM_CONF_LICENSE_FILES = LICENSE
ASAHI_ALSA_UCM_CONF_DEPENDENCIES = alsa-ucm-conf

define ASAHI_ALSA_UCM_CONF_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/usr/share/alsa/
	rsync -arv $(@D)/ucm* $(TARGET_DIR)/usr/share/alsa/
endef

$(eval $(generic-package))
