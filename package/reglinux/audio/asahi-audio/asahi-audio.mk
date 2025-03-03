################################################################################
#
# asahi-audio
#
################################################################################

ASAHI_AUDIO_VERSION = v3.0
ASAHI_AUDIO_SITE = $(call github,AsahiLinux,asahi-audio,$(ASAHI_AUDIO_VERSION))
ASAHI_AUDIO_LICENSE = BSD-3-Clause
ASAHI_AUDIO_LICENSE_FILES = LICENSE
ASAHI_AUDIO_DEPENDENCIES = pipewire wireplumber alsa-ucm-conf asahi-alsa-ucm-conf

$(eval $(generic-package))
