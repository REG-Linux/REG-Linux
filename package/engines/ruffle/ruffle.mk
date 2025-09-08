################################################################################
#
# ruffle
#
################################################################################

RUFFLE_VERSION = nightly-2025-08-31
RUFFLE_SITE = $(call github,ruffle-rs,ruffle,$(RUFFLE_VERSION))
RUFFLE_LICENSE = GPLv2
RUFFLE_DEPENDENCIES = host-rustc host-rust-bin eudev alsa-lib

RUFFLE_CARGO_INSTALL_OPTS = --path desktop/

define RUFFLE_DESKTOP_BINARY_POST_PROCESS
       mv $(TARGET_DIR)/usr/bin/ruffle_desktop $(TARGET_DIR)/usr/bin/ruffle
       $(TARGET_STRIP) $(TARGET_DIR)/usr/bin/ruffle
endef

define RUFFLE_INSTALL_EVMAPY
	mkdir -p $(TARGET_DIR)/usr/share/evmapy
	cp $(BR2_EXTERNAL_REGLINUX_PATH)/package/engines/ruffle/flash.ruffle.keys \
        $(TARGET_DIR)/usr/share/evmapy
endef

RUFFLE_POST_INSTALL_TARGET_HOOKS += RUFFLE_DESKTOP_BINARY_POST_PROCESS
RUFFLE_POST_INSTALL_TARGET_HOOKS += RUFFLE_INSTALL_EVMAPY

$(eval $(rust-package))
