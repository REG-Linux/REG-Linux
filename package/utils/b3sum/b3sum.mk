################################################################################
#
# b3sum
#
################################################################################

B3SUM_VERSION = 1.8.2
B3SUM_SITE = $(call github,BLAKE3-team,BLAKE3,$(B3SUM_VERSION))
B3SUM_LICENSE = Apache-2.0 or Apache-2.0 with exceptions or CC0-1.0
B3SUM_LICENSE_FILES = LICENSE_A2 LICENSE_A2LLVM LICENSE_CC0

B3SUM_SUBDIR = b3sum
HOST_B3SUM_SUBDIR = b3sum

define HOST_B3SUM_INSTALL_CMDS
	cd $(@D)/$(HOST_B3SUM_SUBDIR) && \
	$(HOST_MAKE_ENV) \
		$(HOST_CONFIGURE_OPTS) \
		$(HOST_PKG_CARGO_ENV) \
		$(HOST_B3SUM_CARGO_ENV) \
		cargo install \
			--offline \
			--root $(HOST_DIR) \
			--path ./ \
			--bins \
			--force \
			--locked \
			$(HOST_B3SUM_CARGO_INSTALL_OPTS)
endef

define B3SUM_INSTALL_TARGET_CMDS
	cd $(@D)/$(B3SUM_SUBDIR) && \
	$(TARGET_MAKE_ENV) \
		$(TARGET_CONFIGURE_OPTS) \
		$(PKG_CARGO_ENV) \
		$(B3SUM_CARGO_ENV) \
		cargo install \
			--offline \
			--root $(TARGET_DIR)/usr/ \
			--path ./ \
			--bins \
			--no-track \
			--force \
			--locked \
			-Z target-applies-to-host \
			$(B3SUM_CARGO_INSTALL_OPTS)
endef

$(eval $(cargo-package))
$(eval $(host-cargo-package))
