################################################################################
#
# 86Box emulator
#
################################################################################
# Version.: Release on Sep 1, 2024
86BOX_VERSION = v4.2.1
86BOX_SITE = https://github.com/86Box/86Box
86BOX_SITE_METHOD=git
86BOX_LICENSE = GPLv3
86BOX_DEPENDENCIES = rtmidi libsndfile slirp fluidsynth openal

86BOX_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release -DRELEASE=ON

# Disable QT if we don't have it
ifeq ($(BR2_PACKAGE_REGLINUX_HAS_QT6),y)
86BOX_CONF_OPTS += -DQT=ON -DUSE_QT6=ON
86BOX_DEPENDENCIES += reglinux-qt6
else
86BOX_CONF_OPTS += -DQT=OFF
endif

# Use "new" dynareec for ARMv7 / AArch64
ifeq ($(BR2_arm)$(BR2_aarch64),y)
86BOX_CONF_OPTS += -DNEW_DYNAREC=ON
else ifeq ($(BR2_x86_64),y)
86BOX_CONF_OPTS += -DDYNAREC=ON
else
86BOX_CONF_OPTS += -DDYNAREC=OFF
endif

$(eval $(cmake-package))
