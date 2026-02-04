################################################################################
#
# ioquake3
#
################################################################################
# Version: Commits on Dec 28, 2025
IOQUAKE3_VERSION = 3ef30e759eac79f7e3f98ee495accc76c9807f79
IOQUAKE3_SITE = $(call github,ioquake,ioq3,$(IOQUAKE3_VERSION))
IOQUAKE3_LICENSE = GPL-2.0
IOQUAKE3_LICENSE_FILE = COPYING.txt

IOQUAKE3_DEPENDENCIES = sdl2 libogg libvorbis opus opusfile jpeg libcurl

IOQUAKE3_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release
IOQUAKE3_CONF_OPTS += -DBUILD_SERVER=OFF
IOQUAKE3_CONF_OPTS += -DBUILD_SHARED_LIBS=OFF
IOQUAKE3_CONF_OPTS += -DBUILD_STATIC_LIBS=ON
IOQUAKE3_CONF_OPTS += -DUSE_INTERNAL_LIBS=OFF
IOQUAKE3_CONF_OPTS += -DCMAKE_INSTALL_PREFIX="/usr/ioquake3/"

define IOQUAKE3_EVMAPY
	mkdir -p $(TARGET_DIR)/usr/share/evmapy
	cp $(BR2_EXTERNAL_REGLINUX_PATH)/package/ports/ioquake3/quake3.keys \
	    $(TARGET_DIR)/usr/share/evmapy
endef

IOQUAKE3_POST_INSTALL_TARGET_HOOKS += IOQUAKE3_EVMAPY

$(eval $(cmake-package))
