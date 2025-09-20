################################################################################
#
# DuckStation Qt (AppImage) - Rolling release
#
################################################################################
DUCKSTATION_VERSION = v0.1-9669
ifeq ($(BR2_arm),y)
DUCKSTATION_SOURCE = DuckStation-armhf.AppImage
else ifeq ($(BR2_aarch64),y)
DUCKSTATION_SOURCE = DuckStation-arm64.AppImage
else ifeq ($(BR2_x86_x86_64_v3),y)
DUCKSTATION_SOURCE = DuckStation-x64.AppImage
else ifeq ($(BR2_x86_64),y)
DUCKSTATION_SOURCE = DuckStation-x64-SSE2.AppImage
endif
DUCKSTATION_SITE = https://github.com/stenzek/duckstation/releases/download/$(DUCKSTATION_VERSION)
DUCKSTATION_LICENSE = CC-BY-NC-ND

define DUCKSTATION_EXTRACT_CMDS
        mkdir -p $(@D) && \
        cd $(@D) && \
        cp $(DL_DIR)/$(DUCKSTATION_DL_SUBDIR)/$(DUCKSTATION_SOURCE) $(@D)/
endef

define DUCKSTATION_INSTALL_TARGET_CMDS
	$(INSTALL) -D -m 0755 $(@D)/$(DUCKSTATION_SOURCE) $(TARGET_DIR)/usr/duckstation/DuckStation.AppImage

	# evmap config
	mkdir -p $(TARGET_DIR)/usr/share/evmapy
	cp $(BR2_EXTERNAL_REGLINUX_PATH)/package/emulators/duckstation/psx.duckstation.keys \
	    $(TARGET_DIR)/usr/share/evmapy
endef

$(eval $(generic-package))
