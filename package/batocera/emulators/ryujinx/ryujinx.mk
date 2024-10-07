################################################################################
#
# ryujinx
#
################################################################################

RYUJINX_VERSION = r.dc545c3
ifeq ($(BR2_x86_64),y)
RYUJINX_SOURCE = ryujinx-$(RYUJINX_VERSION)-linux_x64.tar.gz
else
RYUJINX_SOURCE = ryujinx-$(RYUJINX_VERSION)-linux_arm64.tar.gz
endif
RYUJINX_SITE = https://github.com/ryujinx-mirror/ryujinx/releases/download/$(RYUJINX_VERSION)
RYUJINX_LICENSE = MIT
RYUJINX_DEPENDENCIES = sdl2 openal hicolor-icon-theme adwaita-icon-theme librsvg

define RYUJINX_EXTRACT_CMDS
	mkdir -p $(@D)/target && cd $(@D)/target && \
	    tar xf $(DL_DIR)/$(RYUJINX_DL_SUBDIR)/$(RYUJINX_SOURCE)
endef

define RYUJINX_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/usr/ryujinx
	cp -pr $(@D)/target/* $(TARGET_DIR)/usr/ryujinx

	# alias, for compat, remove
	rm $(TARGET_DIR)/usr/ryujinx/Ryujinx.Ava

	# evmap config
	mkdir -p $(TARGET_DIR)/usr/share/evmapy
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/emulators/ryujinx/switch.ryujinx.keys \
	    $(TARGET_DIR)/usr/share/evmapy
endef

$(eval $(generic-package))
