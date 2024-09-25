################################################################################
#
# amiberry
#
################################################################################

ifeq ($(BR2_x86_64),y)
AMIBERRY_VERSION = preview-v6.3.4
else
AMIBERRY_VERSION = v5.7.4
endif
AMIBERRY_SITE = $(call github,BlitterStudio,amiberry,$(AMIBERRY_VERSION))
AMIBERRY_LICENSE = GPLv3
AMIBERRY_DEPENDENCIES =  sdl2 sdl2_image sdl2_ttf mpg123 libxml2 libmpeg2 flac
AMIBERRY_DEPENDENCIES += libpng libserialport libportmidi libzlib libcapsimage
AMIBERRY_SUPPORTS_IN_SOURCE_BUILD = NO

AMIBERRY_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release -DWITH_LTO=ON

define AMIBERRY_INSTALL_TARGET_CMDS
	# Strip and install binary
	$(TARGET_STRIP) $(@D)/buildroot-build/amiberry
	$(INSTALL) -D $(@D)/buildroot-build/amiberry $(TARGET_DIR)/usr/bin/amiberry

	# Create config and nvram directories, copy default config
	mkdir -p $(TARGET_DIR)/usr/share/reglinux/datainit/system/configs/amiberry/conf
	cp -prn $(@D)/conf/amiberry.conf        $(TARGET_DIR)/usr/share/reglinux/datainit/system/configs/amiberry/conf/
	cp -prn $(@D)/conf/gamecontrollerdb.txt $(TARGET_DIR)/usr/share/reglinux/datainit/system/configs/amiberry/conf/
	mkdir -p $(TARGET_DIR)/usr/share/reglinux/datainit/saves/amiga/nvram

	# Copy AROS (open source alternative BIOS)
	mkdir -p $(TARGET_DIR)/usr/share/reglinux/datainit/bios/amiga
	cp -prn $(@D)/kickstarts/aros-ext.bin $(TARGET_DIR)/usr/share/reglinux/datainit/bios/amiga/
	cp -prn $(@D)/kickstarts/aros-rom.bin $(TARGET_DIR)/usr/share/reglinux/datainit/bios/amiga/

	# Copy data and whdboot folders
	mkdir -p $(TARGET_DIR)/usr/share/amiberry
	cp -pr $(@D)/whdboot $(TARGET_DIR)/usr/share/amiberry/
	cp -pr $(@D)/data $(TARGET_DIR)/usr/share/amiberry/

	# Copy plugins
	mkdir -p $(TARGET_DIR)/usr/share/amiberry/plugins
	$(INSTALL) -D $(@D)/buildroot-build/plugins/* $(TARGET_DIR)/usr/share/amiberry/plugins
endef

define AMIBERRY_EVMAP
	mkdir -p $(TARGET_DIR)/usr/share/evmapy
	cp -prn $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/emulators/amiberry/controllers/amiga500.amiberry.keys \
		$(TARGET_DIR)/usr/share/evmapy
	cp -prn $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/emulators/amiberry/controllers/amiga1200.amiberry.keys \
		$(TARGET_DIR)/usr/share/evmapy
	cp -prn $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/emulators/amiberry/controllers/amigacd32.amiberry.keys \
		$(TARGET_DIR)/usr/share/evmapy
endef

AMIBERRY_POST_INSTALL_TARGET_HOOKS = AMIBERRY_EVMAP

$(eval $(cmake-package))
