################################################################################
#
# libretro-holani
#
################################################################################

LIBRETRO_HOLANI_VERSION = 0.9.6-1
LIBRETRO_HOLANI_SITE = $(call github,lleny,holani-retro,$(LIBRETRO_HOLANI_VERSION))
LIBRETRO_HOLANI_LICENSE = GPLv3
LIBRETRO_HOLANI_DEPENDENCIES = host-rustc host-rust-bin clang llvm

LIBRETRO_HOLANI_CARGO_MODE = $(if $(BR2_ENABLE_DEBUG),debug,release)
LIBRETRO_HOLANI_BIN_DIR = target/$(RUSTC_TARGET_NAME)/$(LIBRETRO_HOLANI_CARGO_MODE)

# Bindgen needs clang path
LIBRETRO_HOLANI_CARGO_ENV = BINDGEN_EXTRA_CLANG_ARGS="-I$(HOST_DIR)/usr/lib/clang/$(CLANG_VERSION_MAJOR)/include/" LIBCLANG_PATH="$(HOST_DIR)/usr/lib"

define LIBRETRO_HOLANI_INSTALL_TARGET_CMDS
    $(INSTALL) -D $(@D)/$(LIBRETRO_HOLANI_BIN_DIR)/libholani.so \
             $(TARGET_DIR)/usr/lib/libretro/holani_libretro.so
    $(INSTALL) -D $(@D)/res/holani_libretro.info \
    	     $(TARGET_DIR)/usr/share/libretro/info/holani_libretro.info
endef

$(eval $(cargo-package))
