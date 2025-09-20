################################################################################
#
# DuckStation Mini (AppImage) - Rolling release
#
################################################################################
DUCKSTATION_MINI_VERSION = v0.1-9669
ifeq ($(BR2_arm),y)
DUCKSTATION_MINI_SOURCE = DuckStation-Mini-armhf.AppImage
else ifeq ($(BR2_aarch64),y)
DUCKSTATION_MINI_SOURCE = DuckStation-Mini-arm64.AppImage
endif
DUCKSTATION_MINI_SITE = https://github.com/stenzek/duckstation/releases/download/$(DUCKSTATION_MINI_VERSION)
DUCKSTATION_MINI_LICENSE = CC-BY-NC-ND
DUCKSTATION_MINI_DEPENDENCIES = gmp

define DUCKSTATION_MINI_EXTRACT_CMDS
	mkdir -p $(@D) && \
	cd $(@D) && \
	cp $(DL_DIR)/$(DUCKSTATION_MINI_DL_SUBDIR)/$(DUCKSTATION_MINI_SOURCE) $(@D)/
endef

define DUCKSTATION_MINI_INSTALL_TARGET_CMDS
	$(INSTALL) -D -m 0755 $(@D)/$(DUCKSTATION_MINI_SOURCE) $(TARGET_DIR)/usr/duckstation/DuckStation.AppImage

	# evmap config
	mkdir -p $(TARGET_DIR)/usr/share/evmapy
	cp $(BR2_EXTERNAL_REGLINUX_PATH)/package/emulators/duckstation-mini/psx.duckstation.keys \
	    $(TARGET_DIR)/usr/share/evmapy
endef

$(eval $(generic-package))
