################################################################################
#
# ayn-alsa-ucm-conf
#
################################################################################

# Version : Commits on Feb 24, 2025
AYN_ALSA_UCM_CONF_VERSION = 39a2034f56bc990059cf20d3d6ef3e85fdb0e924
AYN_ALSA_UCM_CONF_SITE = https://github.com/AYNTechnologies/alsa-ucm-conf.git
AYN_ALSA_UCM_CONF_SITE_METHOD = git
AYN_ALSA_UCM_CONF_LICENSE = BSD-3-Clause
AYN_ALSA_UCM_CONF_LICENSE_FILES = LICENSE
AYN_ALSA_UCM_CONF_DEPENDENCIES = alsa-ucm-conf

define AYN_ALSA_UCM_CONF_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/usr/share/alsa/
	rsync -arv $(@D)/ucm* $(TARGET_DIR)/usr/share/alsa/
endef

$(eval $(generic-package))
