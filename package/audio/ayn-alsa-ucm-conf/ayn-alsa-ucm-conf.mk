################################################################################
#
# ayn-alsa-ucm-conf
#
################################################################################

# Version : Commits on Apr 15, 2026
AYN_ALSA_UCM_CONF_VERSION = 52b6ae98b7cd01e35ab6d193f953394dcefe5c0e
AYN_ALSA_UCM_CONF_SITE = https://github.com/AYNTechnologies/alsa-ucm-conf.git
AYN_ALSA_UCM_CONF_SITE_METHOD = git
AYN_ALSA_UCM_CONF_LICENSE = BSD-3-Clause
AYN_ALSA_UCM_CONF_LICENSE_FILES = LICENSE
AYN_ALSA_UCM_CONF_DEPENDENCIES = alsa-ucm-conf

AYN_ALSA_UCM_CONF_UCM_DIR = $(TARGET_DIR)/usr/share/alsa/ucm2

# The AYN repository is a full alsa-ucm-conf fork (v1.2.15.3 + AYN files).
# Only install the AYN files, so the newer, patched alsa-ucm-conf stays intact.
define AYN_ALSA_UCM_CONF_INSTALL_TARGET_CMDS
	mkdir -p $(AYN_ALSA_UCM_CONF_UCM_DIR)/conf.d/sm8550 $(AYN_ALSA_UCM_CONF_UCM_DIR)/conf.d/sm8750
	rsync -a $(@D)/ucm2/AYN/ $(AYN_ALSA_UCM_CONF_UCM_DIR)/AYN/
	cp -a $(@D)/ucm2/conf.d/sm8550/SM8550-AYN.conf $(AYN_ALSA_UCM_CONF_UCM_DIR)/conf.d/sm8550/
	cp -a $(@D)/ucm2/conf.d/sm8750/SM8750-AYN.conf $(AYN_ALSA_UCM_CONF_UCM_DIR)/conf.d/sm8750/
endef

# Our SM8550 device trees name the Odin 2 card "AYN-Odin2" (AYN's kernel uses
# "SM8550-AYN"). ucm.conf only matches conf.d/<driver>/<card long name>.conf:
# the long name is the card name, or the DMI vendor-product- string under an
# EFI boot. The Portal and Mini names are a best guess; check /proc/asound/cards.
# The Thor keeps ROCKNIX's own config (internal DMIC + amp settings).
ifeq ($(BR2_PACKAGE_SYSTEM_TARGET_SM8550),y)
define AYN_ALSA_UCM_CONF_LINK_ODIN2
	for name in AYN-Odin2 ayn-AYNOdin2- ayn-AYNOdin2Portal- ayn-AYNOdin2Mini-; do \
		ln -sf ../../AYN/SM8550/SM8550-AYN.conf \
			$(AYN_ALSA_UCM_CONF_UCM_DIR)/conf.d/sm8550/$${name}.conf; \
	done
endef
AYN_ALSA_UCM_CONF_POST_INSTALL_TARGET_HOOKS += AYN_ALSA_UCM_CONF_LINK_ODIN2
endif

$(eval $(generic-package))
