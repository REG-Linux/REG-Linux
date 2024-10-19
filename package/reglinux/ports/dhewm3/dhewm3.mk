################################################################################
#
# dhewm3
#
################################################################################

DHEWM3_VERSION = 1.5.4
DHEWM3_SITE = https://github.com/dhewm/dhewm3
DHEWM3_LICENSE = GPLv3
DHEWM3_LICENSE_FILES = COPYING.txt
DHEWM3_SITE_METHOD=git
DHEWM3_DEPENDENCIES = host-libjpeg libcurl libogg libvorbis openal sdl2 zlib 
DHEWM3_SUPPORTS_IN_SOURCE_BUILD = NO

DHEWM3_SUBDIR = neo

DHEWM3_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release
DHEWM3_CONF_OPTS += -DBUILD_SHARED_LIBS=OFF
DHEWM3_CONF_OPTS += -DBUILD_STATIC_LIBS=ON
DHEWM3_CONF_OPTS += -DENABLE_TEST=OFF

define DHEWM3_EVMAPY
	mkdir -p $(TARGET_DIR)/usr/share/evmapy
	cp -prn $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/emulators/dhewm3/doom3.dhewm3.keys \
		$(TARGET_DIR)/usr/share/evmapy
endef

DHEWM3_POST_INSTALL_TARGET_HOOKS = DHEWM3_EVMAPY

$(eval $(cmake-package))
