################################################################################
#
# gopher64
#
################################################################################

GOPHER64_VERSION = v1.1.40
GOPHER64_SITE = https://github.com/gopher64/gopher64.git
GOPHER64_SITE_METHOD = git
GOPHER64_GIT_SUBMODULES = YES
GOPHER64_LICENSE = GPLv2
GOPHER64_DEPENDENCIES = alsa-lib libgl wayland xwayland host-clang host-cmake host-pkgconf \
	fontconfig libxkbcommon vulkan-headers vulkan-loader \
	xlib_libXcursor xlib_libXext xlib_libXfixes xlib_libXi xlib_libXrandr \
	xlib_libXScrnSaver xlib_libXtst

# Upstream declares rust-version 1.99.0; it builds fine with our toolchain.
GOPHER64_CARGO_BUILD_OPTS = --ignore-rust-version
GOPHER64_CARGO_INSTALL_OPTS = --path ./ --ignore-rust-version

# bindgen must use host-clang's libclang with its builtin headers (stdbool.h)
# and the target sysroot, like pocketHLE/inputplumber; otherwise it relies on
# whatever clang the build host has (none in the Jenkins container).
# It also does not find the cross toolchain's libstdc++ headers
# (parallel-rdp/interface.hpp includes <cstdint>), so point it at them.
# -cxx-isystem keeps them out of C parses: libstdc++'s stdatomic.h would
# otherwise shadow clang's for sse2neon.h.
GOPHER64_CXX_INCLUDE = $(firstword $(wildcard $(HOST_DIR)/$(GNU_TARGET_NAME)/include/c++/*))
GOPHER64_CARGO_ENV = \
	LIBCLANG_PATH="$(HOST_DIR)/usr/lib" \
	BINDGEN_EXTRA_CLANG_ARGS="--sysroot=$(STAGING_DIR) \
		-I$(HOST_DIR)/usr/lib/clang/$(CLANG_VERSION_MAJOR)/include \
		-cxx-isystem $(GOPHER64_CXX_INCLUDE) -cxx-isystem $(GOPHER64_CXX_INCLUDE)/$(GNU_TARGET_NAME)"

define GOPHER64_BINARY_POST_PROCESS
       $(TARGET_STRIP) $(TARGET_DIR)/usr/bin/gopher64
endef

GOPHER64_POST_INSTALL_TARGET_HOOKS += GOPHER64_BINARY_POST_PROCESS

$(eval $(rust-package))
