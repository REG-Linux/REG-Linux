################################################################################
#
# asahi-audio
#
################################################################################

ASAHI_AUDIO_VERSION = v2.6
ASAHI_AUDIO_SITE = $(call github,AsahiLinux,asahi-audio,$(ASAHI_AUDIO_VERSION))
ASAHI_AUDIO_LICENSE = BSD-3-Clause
ASAHI_AUDIO_LICENSE_FILES = LICENSE
ASAHI_AUDIO_DEPENDENCIES = pipewire wireplumber alsa-ucm-conf asahi-alsa-ucm-conf

define ASAHI_AUDIO_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/usr/share
	cd $(@D) && DESTDIR=$(TARGET_DIR) make install
endef
$(eval $(generic-package))
