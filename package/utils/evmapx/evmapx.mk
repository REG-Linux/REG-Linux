################################################################################
#
# evmapx
#
################################################################################

EVMAPX_VERSION = fda49723aecec4a3f48dc4cc7459c21628a72620
EVMAPX_TOKEN = $(shell cat /build/gh_token)
EVMAPX_SITE = https://$(EVMAPX_TOKEN)@github.com/REG-Linux/evmapx
EVMAPX_SITE_METHOD = git
EVMAPX_LICENSE = MIT
EVMAPX_LICENSE_FILES = LICENSE

RUSTC_TARGET_PROFILE = $(if $(BR2_ENABLE_DEBUG),debug,release)
EVMAPX_LOCATION = target/$(RUSTC_TARGET_NAME)/$(RUSTC_TARGET_PROFILE)

define EVMAPX_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/$(EVMAPX_LOCATION)/evmapx			$(TARGET_DIR)/usr/bin/
endef

$(eval $(cargo-package))
