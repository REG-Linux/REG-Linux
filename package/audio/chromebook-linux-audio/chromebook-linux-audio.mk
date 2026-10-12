################################################################################
#
# chromebook-linux-audio
#
################################################################################
# Version: Commits on May 16, 2026
CHROMEBOOK_LINUX_AUDIO_VERSION = cd3c5f5c73cae02738b3b37e887a4b67579ef74c
CHROMEBOOK_LINUX_AUDIO_SITE = $(call github,WeirdTreeThing,chromebook-linux-audio,$(CHROMEBOOK_LINUX_AUDIO_VERSION))
CHROMEBOOK_LINUX_AUDIO_LICENSE = BSD-3-Clause
CHROMEBOOK_LINUX_AUDIO_LICENSE_FILES = LICENSE

CHROMEBOOK_LINUX_AUDIO_DEPENDENCIES += alsa-ucm-conf alsa-utils
CHROMEBOOK_LINUX_AUDIO_DEPENDENCIES += alllinuxfirmwares sound-open-firmware
CHROMEBOOK_LINUX_AUDIO_DEPENDENCIES += chromebook-ucm-conf

define CHROMEBOOK_LINUX_AUDIO_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/lib/firmware/amd/sof/community
	mkdir -p $(TARGET_DIR)/lib/firmware/amd/sof-tplg
	rsync -arv $(@D)/blobs/mdn/fw/ $(TARGET_DIR)/lib/firmware/amd/sof/community/
	rsync -arv $(@D)/blobs/mdn/tplg/ $(TARGET_DIR)/lib/firmware/amd/sof-tplg/
endef

$(eval $(generic-package))
