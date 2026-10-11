################################################################################
#
# pocketHLE
#
################################################################################

POCKETHLE_VERSION = v0.3.1
POCKETHLE_SITE = https://github.com/j92580498-max/PocketHLE.git
POCKETHLE_SITE_METHOD = git
POCKETHLE_GIT_SUBMODULES = YES
POCKETHLE_LICENSE = GPLv2
POCKETHLE_DEPENDENCIES = alsa-lib libglib2 libgtk3 host-clang #boost openal sdl2

# VENDOR/unicorn-engine-sys's build.rs runs bindgen (libclang) against
# unicorn/platform.h to generate Rust bindings. Without LIBCLANG_PATH
# pointing bindgen at host-clang's own libclang.so, and without
# BINDGEN_EXTRA_CLANG_ARGS giving it both its own resource-dir include
# path (stdbool.h/stdarg.h/... - clang's builtin headers, not glibc's)
# and the target sysroot for glibc's own headers, bindgen's clang
# invocation can't even parse the standard C prelude - "fatal error:
# 'stdbool.h' file not found" on aarch64 (x86_64 apparently tolerates
# whatever ambient system headers bindgen falls back to finding, but
# don't rely on that continuing to be true). Same pattern already
# established in this tree for other rust-package/bindgen combinations -
# see package/utils/inputplumber/inputplumber.mk.
POCKETHLE_CARGO_ENV += LIBCLANG_PATH="$(HOST_DIR)/usr/lib" BINDGEN_EXTRA_CLANG_ARGS="--sysroot=$(STAGING_DIR) -I$(HOST_DIR)/usr/lib/clang/$(CLANG_VERSION_MAJOR)/include/"

define POCKETHLE_INSTALL_TARGET_CMDS
        $(INSTALL) -D -m 0755 $(@D)/target/$(RUSTC_TARGET_NAME)/$(RUSTC_TARGET_PROFILE)/pockethle \
                $(TARGET_DIR)/usr/bin/pockethle
        $(INSTALL) -D -m 0755 $(@D)/target/$(RUSTC_TARGET_NAME)/$(RUSTC_TARGET_PROFILE)/pockethle-gui \
                $(TARGET_DIR)/usr/bin/pockethle-gui
	# TODO additional stuff we might need
endef

$(eval $(rust-package))
