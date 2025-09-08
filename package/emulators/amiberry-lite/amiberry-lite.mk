################################################################################
#
# amiberry
#
################################################################################

AMIBERRY_LITE_VERSION = v5.8.11
AMIBERRY_LITE_SITE = $(call github,BlitterStudio,amiberry-lite,$(AMIBERRY_LITE_VERSION))
AMIBERRY_LITE_LICENSE = GPLv3
AMIBERRY_LITE_DEPENDENCIES =  sdl2 sdl2_image sdl2_ttf mpg123 libxml2 libmpeg2 flac
AMIBERRY_LITE_DEPENDENCIES += libpng libserialport libportmidi zlib libcapsimage
AMIBERRY_LITE_DEPENDENCIES += libenet
AMIBERRY_LITE_SUPPORTS_IN_SOURCE_BUILD = NO

AMIBERRY_LITE_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release -DWITH_LTO=ON

define AMIBERRY_LITE_INSTALL_TARGET_CMDS
	# Strip and install binary
	$(TARGET_STRIP) $(@D)/buildroot-build/amiberry-lite
	$(INSTALL) -D $(@D)/buildroot-build/amiberry-lite $(TARGET_DIR)/usr/bin/amiberry

	# Create config and nvram directories, copy default config
	mkdir -p $(TARGET_DIR)/usr/share/reglinux/datainit/saves/amiga/nvram
	mkdir -p $(TARGET_DIR)/usr/share/reglinux/datainit/system/configs/amiberry/conf
	mkdir -p $(TARGET_DIR)/usr/share/reglinux/datainit/system/configs/amiberry/plugins

	# Copy AROS (open source alternative BIOS)
	mkdir -p $(TARGET_DIR)/usr/share/reglinux/datainit/bios/amiga
	cp -prn $(@D)/roms/aros-ext.bin $(TARGET_DIR)/usr/share/reglinux/datainit/bios/amiga/
	cp -prn $(@D)/roms/aros-rom.bin $(TARGET_DIR)/usr/share/reglinux/datainit/bios/amiga/

	# Copy data and whdboot folders
	mkdir -p $(TARGET_DIR)/usr/share/amiberry
	cp -pr $(@D)/whdboot $(TARGET_DIR)/usr/share/amiberry/
	cp -pr $(@D)/data $(TARGET_DIR)/usr/share/amiberry/
	cp -p $(@D)/data/AmigaTopaz.ttf $(TARGET_DIR)/usr/share/amiberry/data
endef

define AMIBERRY_LITE_EVMAP
	mkdir -p $(TARGET_DIR)/usr/share/evmapy
	cp -f $(BR2_EXTERNAL_REGLINUX_PATH)/package/emulators/amiberry-lite/evmapy/* \
		$(TARGET_DIR)/usr/share/evmapy
endef

AMIBERRY_LITE_POST_INSTALL_TARGET_HOOKS = AMIBERRY_LITE_EVMAP

$(eval $(cmake-package))
