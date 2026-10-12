################################################################################
#
# DuckStation Qt (AppImage) - Rolling release
#
################################################################################
DUCKSTATION_VERSION = v0.1-11894
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
	# Expose the AppImage under its emulator name in /usr/bin so regmsgd's
	# capability scan detects it (it only scans /usr/bin) and the launcher
	# resolver honours psx.emulator=duckstation instead of falling back to
	# libretro. The generator's BIN still points at the real AppImage path.
	ln -sf /usr/duckstation/DuckStation.AppImage $(TARGET_DIR)/usr/bin/duckstation
endef

$(eval $(generic-package))
