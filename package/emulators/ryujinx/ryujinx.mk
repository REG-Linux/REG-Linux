################################################################################
#
# ryujinx
#
################################################################################

RYUJINX_VERSION = 1.3.3
ifeq ($(BR2_x86_64),y)
RYUJINX_SOURCE = ryujinx-$(RYUJINX_VERSION)-linux_x64.tar.gz
else ifeq ($(BR2_aarch64),y)
RYUJINX_SOURCE = ryujinx-$(RYUJINX_VERSION)-linux_arm64.tar.gz
endif
RYUJINX_SITE = https://git.ryujinx.app/api/v4/projects/1/packages/generic/Ryubing/$(RYUJINX_VERSION)
RYUJINX_LICENSE = MIT
#RYUJINX_DEPENDENCIES = sdl2 openal hicolor-icon-theme adwaita-icon-theme librsvg

define RYUJINX_EXTRACT_CMDS
	mkdir -p $(@D)/target && cd $(@D)/target && \
	    tar xf $(DL_DIR)/$(RYUJINX_DL_SUBDIR)/$(RYUJINX_SOURCE)
endef

define RYUJINX_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/usr/ryujinx
	cp -pr $(@D)/target/publish/* $(TARGET_DIR)/usr/ryujinx/

	# evmap config
	mkdir -p $(TARGET_DIR)/usr/share/evmapy
	cp $(BR2_EXTERNAL_REGLINUX_PATH)/package/emulators/ryujinx/switch.ryujinx.keys \
	    $(TARGET_DIR)/usr/share/evmapy
endef

$(eval $(generic-package))
