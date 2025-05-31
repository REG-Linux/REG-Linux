################################################################################
#
# zmusic
#
################################################################################
ZMUSIC_VERSION = 1.1.14
ZMUSIC_SITE = $(call github,ZDoom,ZMusic,$(ZMUSIC_VERSION))
ZMUSIC_LICENSE = GPLv3
ZMUSIC_INSTALL_STAGING = YES
ZMUSIC_DEPENDENCIES = zlib mpg123 libsndfile alsa-lib libglib2 host-zmusic
ZMUSIC_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release

ifeq ($(BR2_PACKAGE_FLUIDSYNTH),y)
ZMUSIC_DEPENDENCIES += fluidsynth
endif

define ZMUSIC_INSTALL_TARGET_CMDS
    cp -d $(@D)/source/libzmusic* $(TARGET_DIR)/usr/lib/
endef

$(eval $(cmake-package))

HOST_ZMUSIC_DEPENDENCIES = host-zlib host-libglib2
$(eval $(host-cmake-package))
