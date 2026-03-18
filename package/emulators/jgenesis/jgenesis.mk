################################################################################
#
# jgenesis
#
################################################################################
# Version: Release on Mar 5, 2025
JGENESIS_VERSION = v0.11.3
JGENESIS_SITE = $(call github,jsgroth,jgenesis,$(JGENESIS_VERSION))
JGENESIS_LICENSE = MIT
JGENESIS_LICENSE_FILES = LICENSE
# SDL3 is built from source by cargo/cmake (sdl3-build-from-source default feature).
# xlib_libX11/xlib_libXrandr are needed by the xrandr-rs crate.
JGENESIS_DEPENDENCIES = host-cmake xlib_libX11 xlib_libXrandr

RUSTC_TARGET_PROFILE = $(if $(BR2_ENABLE_DEBUG),debug,release)

# PKG_CONFIG_ALLOW_CROSS=1: the pkg_config Rust crate refuses pkg-config when
#   cross-compiling by default; this enables it for xrandr-rs and others.
# CMAKE_TOOLCHAIN_FILE: when sdl3-sys builds SDL3 from source via cmake, this
#   ensures cmake uses the buildroot sysroot, cross-compiler and finds target
#   libraries (Wayland, drm, ALSA...) correctly instead of using host paths.
JGENESIS_CARGO_ENV = \
	PKG_CONFIG_ALLOW_CROSS=1 \
	PKG_CONFIG=$(HOST_DIR)/usr/bin/pkg-config \
	PKG_CONFIG_SYSROOT_DIR=$(STAGING_DIR) \
	PKG_CONFIG_LIBDIR=$(STAGING_DIR)/usr/lib/pkgconfig:$(STAGING_DIR)/usr/share/pkgconfig \
	CMAKE_TOOLCHAIN_FILE=$(HOST_DIR)/share/buildroot/toolchainfile.cmake

# Build jgenesis-cli and jgenesis-gui only.
# Do NOT use --no-default-features: the default sdl3-build-from-source feature
# builds SDL3 from source via cmake, avoiding host-SDL3 pkg-config contamination
# that causes "-L /usr/local/lib" in the linker command.
JGENESIS_CARGO_BUILD_OPTS  = --package jgenesis-cli
JGENESIS_CARGO_BUILD_OPTS += --package jgenesis-gui

# The vendored sdl3 crate's build.rs unconditionally emits
# "cargo:rustc-link-search=/usr/local/lib" on Linux targets, which causes
# the buildroot cross-compiler wrapper to reject the unsafe host path.
# Remove that line from the vendor tree before building.
define JGENESIS_REMOVE_SDL3_USR_LOCAL_LINKPATH
	$(SED) '/cfg.*target_os.*linux.*openbsd.*freebsd/{N;/rustc-link-search.*usr.local.lib/d}' $(@D)/VENDOR/sdl3/build.rs
	$(SED) 's/"files":{[^}]*}/"files":{}/' $(@D)/VENDOR/sdl3/.cargo-checksum.json
endef
JGENESIS_POST_PATCH_HOOKS += JGENESIS_REMOVE_SDL3_USR_LOCAL_LINKPATH

# Override BUILD_CMDS to clear the cargo build-script cache before building.
# Cargo caches build script outputs between failed attempts; stale outputs from
# before env-var fixes were applied would otherwise persist and keep emitting
# the wrong link-search paths.
define JGENESIS_BUILD_CMDS
	rm -rf $(@D)/target/$(RUSTC_TARGET_NAME)/$(RUSTC_TARGET_PROFILE)/build
	cd $(@D) && \
	$(TARGET_MAKE_ENV) \
	$(TARGET_CONFIGURE_OPTS) \
	$(PKG_CARGO_ENV) \
	$(JGENESIS_CARGO_ENV) \
	cargo build \
		--offline \
		$(if $(BR2_ENABLE_DEBUG),,--release) \
		--manifest-path Cargo.toml \
		--locked \
		$(JGENESIS_CARGO_BUILD_OPTS)
endef

define JGENESIS_INSTALL_TARGET_CMDS
	$(INSTALL) -D -m 0755 $(@D)/target/$(RUSTC_TARGET_NAME)/$(RUSTC_TARGET_PROFILE)/jgenesis-cli \
		$(TARGET_DIR)/usr/bin/jgenesis-cli
	$(INSTALL) -D -m 0755 $(@D)/target/$(RUSTC_TARGET_NAME)/$(RUSTC_TARGET_PROFILE)/jgenesis-gui \
		$(TARGET_DIR)/usr/bin/jgenesis-gui
endef

$(eval $(cargo-package))
