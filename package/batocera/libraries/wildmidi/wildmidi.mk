################################################################################
#
# WildMIDI
#
################################################################################
# Version.: Release on Apr 11, 2024
WILDMIDI_VERSION = wildmidi-0.4.6
WILDMIDI_SITE =  $(call github,Mindwerks,wildmidi,$(WILDMIDI_VERSION))
WILDMIDI_LICENSE = LGPLv3
WILDMIDI_INSTALL_STAGING = YES

WILDMIDI_CONF_OPTS += -DBUILD_TESTING=OFF -DWANT_STATIC=ON -DWANT_PLAYER=OFF

$(eval $(cmake-package))
