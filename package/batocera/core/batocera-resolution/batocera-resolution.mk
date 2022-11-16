################################################################################
#
# batocera resolution
#
################################################################################

BATOCERA_RESOLUTION_VERSION = 1
BATOCERA_RESOLUTION_LICENSE = GPL
BATOCERA_RESOLUTION_DEPENDENCIES = pciutils
BATOCERA_RESOLUTION_SOURCE=

BATOCERA_RESOLUTION_PATH = $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/core/batocera-resolution/scripts

BATOCERA_SCRIPT_RESOLUTION_TYPE=basic
BATOCERA_SCRIPT_SCREENSHOT_TYPE=basic

ifeq ($(BR2_PACKAGE_RPI_USERLAND),y)
  BATOCERA_SCRIPT_RESOLUTION_TYPE=tvservice
  BATOCERA_SCRIPT_SCREENSHOT_TYPE=tvservice
endif
ifeq ($(BR2_PACKAGE_LIBDRM),y)
  BATOCERA_SCRIPT_RESOLUTION_TYPE=drm
  BATOCERA_SCRIPT_SCREENSHOT_TYPE=drm
endif
ifeq ($(BR2_PACKAGE_XSERVER_XORG_SERVER),y)
  BATOCERA_SCRIPT_RESOLUTION_TYPE=xorg
  BATOCERA_SCRIPT_SCREENSHOT_TYPE=xorg
endif

ifeq ($(BR2_PACKAGE_WAYLAND)$(BR2_PACKAGE_SWAY),yy)
  BATOCERA_SCRIPT_RESOLUTION_TYPE=wayland
  BATOCERA_SCRIPT_SCREENSHOT_TYPE=wayland
endif

# doesn't work on odroidgoa with mali g31_gbm
ifeq ($(BR2_PACKAGE_MALI_G31_GBM),y)
  BATOCERA_SCRIPT_RESOLUTION_TYPE=basic
endif

define BATOCERA_RESOLUTION_INSTALL_TARGET_CMDS
	install -m 0755 $(BATOCERA_RESOLUTION_PATH)/batocera-resolution.$(BATOCERA_SCRIPT_RESOLUTION_TYPE) $(TARGET_DIR)/usr/bin/batocera-resolution
	install -m 0755 $(BATOCERA_RESOLUTION_PATH)/batocera-screenshot.$(BATOCERA_SCRIPT_SCREENSHOT_TYPE) $(TARGET_DIR)/usr/bin/batocera-screenshot
endef

define BATOCERA_RESOLUTION_INSTALL_RG552
	install -m 0755 $(BATOCERA_RESOLUTION_PATH)/batocera-resolution-post-rg552 $(TARGET_DIR)/usr/bin/batocera-resolution-post
endef

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RG552),y)
  BATOCERA_RESOLUTION_POST_INSTALL_TARGET_HOOKS += BATOCERA_RESOLUTION_INSTALL_RG552
endif

define BATOCERA_RESOLUTION_INSTALL_RK3128
        install -m 0755 $(BATOCERA_RESOLUTION_PATH)/batocera-resolution-post-rk3128 $(TARGET_DIR)/usr/bin/batocera-resolution-post
endef

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RK3128),y)
  BATOCERA_RESOLUTION_POST_INSTALL_TARGET_HOOKS += BATOCERA_RESOLUTION_INSTALL_RK3128
endif

define BATOCERA_RESOLUTION_INSTALL_XORG
	mkdir -p $(TARGET_DIR)/etc/X11/xorg.conf.d
	cp -prn $(BR2_EXTERNAL_BATOCERA_PATH)/board/batocera/x86/fsoverlay/etc/X11/xorg.conf.d/20-amdgpu.conf $(TARGET_DIR)/etc/X11/xorg.conf.d/20-amdgpu.conf
	install -m 0755 $(BATOCERA_RESOLUTION_PATH)/batocera-record $(TARGET_DIR)/usr/bin/
endef

ifeq ($(BR2_PACKAGE_XSERVER_XORG_SERVER),y)
  BATOCERA_RESOLUTION_POST_INSTALL_TARGET_HOOKS += BATOCERA_RESOLUTION_INSTALL_XORG
endif

$(eval $(generic-package))