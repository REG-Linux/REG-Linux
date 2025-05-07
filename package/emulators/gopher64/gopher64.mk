################################################################################
#
# gopher64
#
################################################################################

GOPHER64_VERSION = v1.0.16
GOPHER64_SITE = https://github.com/gopher64/gopher64.git
GOPHER64_SITE_METHOD = git
GOPHER64_GIT_SUBMODULES = YES
GOPHER64_LICENSE = GPLv2
ifeq ($(BR2_PACKAGE_REGLINUX_LLVM_BUILD_FROM_SOURCE),y)
GOPHER64_DEPENDENCIES = alsa-lib libgl wayland xwayland host-clang clang
else
GOPHER64_DEPENDENCIES = alsa-lib libgl wayland xwayland reglinux-llvm
endif

GOPHER64_CARGO_INSTALL_OPTS = --path ./

# Fix for cstdint include not found
#GOPHER64_CARGO_ENV = BINDGEN_EXTRA_CLANG_ARGS="-I$(STAGING_DIR)/lib/clang/$(CLANG_VERSION_MAJOR)/include/"

define GOPHER64_BINARY_POST_PROCESS
       $(TARGET_STRIP) $(TARGET_DIR)/usr/bin/gopher64
endef

GOPHER64_POST_INSTALL_TARGET_HOOKS += GOPHER64_BINARY_POST_PROCESS

$(eval $(rust-package))
