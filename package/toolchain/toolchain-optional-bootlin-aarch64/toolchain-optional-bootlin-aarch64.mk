################################################################################
#
# toolchain-optional-bootlin-aarch64
#
################################################################################

HOST_TOOLCHAIN_OPTIONAL_BOOTLIN_AARCH64_ARCH = aarch64
HOST_TOOLCHAIN_OPTIONAL_BOOTLIN_AARCH64_LIBC = glibc
HOST_TOOLCHAIN_OPTIONAL_BOOTLIN_AARCH64_FLAVOR = stable
HOST_TOOLCHAIN_OPTIONAL_BOOTLIN_AARCH64_VERSION = 2025.08-1
HOST_TOOLCHAIN_OPTIONAL_BOOTLIN_AARCH64_FULL_VERSION = $(HOST_TOOLCHAIN_OPTIONAL_BOOTLIN_AARCH64_ARCH)--$(HOST_TOOLCHAIN_OPTIONAL_BOOTLIN_AARCH64_LIBC)--$(HOST_TOOLCHAIN_OPTIONAL_BOOTLIN_AARCH64_FLAVOR)-$(HOST_TOOLCHAIN_OPTIONAL_BOOTLIN_AARCH64_VERSION)
HOST_TOOLCHAIN_OPTIONAL_BOOTLIN_AARCH64_SITE = https://toolchains.bootlin.com/downloads/releases/toolchains/$(HOST_TOOLCHAIN_OPTIONAL_BOOTLIN_AARCH64_ARCH)/tarballs
HOST_TOOLCHAIN_OPTIONAL_BOOTLIN_AARCH64_SOURCE = $(HOST_TOOLCHAIN_OPTIONAL_BOOTLIN_AARCH64_FULL_VERSION).tar.xz

# wrap gcc and g++ with ccache like in gcc package.mk
PKG_GCC_PREFIX="$(HOST_DIR)/lib/gcc-bootlin-aarch64-linux-gnu/bin/aarch64-buildroot-linux-gnu-"

define HOST_TOOLCHAIN_OPTIONAL_BOOTLIN_AARCH64_INSTALL_CMDS
	mkdir -p $(HOST_DIR)/lib/gcc-bootlin-aarch64-linux-gnu/
	cp -a $(@D)/* $(HOST_DIR)/lib/gcc-bootlin-aarch64-linux-gnu
endef

$(eval $(host-generic-package))
