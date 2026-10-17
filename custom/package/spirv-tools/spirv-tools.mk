################################################################################
#
# spirv-tools
#
################################################################################
# reglinux - 1.4.304.0 needed to build spirv-llvm-translator
SPIRV_TOOLS_VERSION = 1.4.357.0

ifeq ($(BR2_PACKAGE_SPIRV_TOOLS_BUILD_FROM_SOURCE),y)

SPIRV_TOOLS_SITE = $(call github,KhronosGroup,SPIRV-Tools,vulkan-sdk-$(SPIRV_TOOLS_VERSION))
SPIRV_TOOLS_LICENSE = Apache-2.0
SPIRV_TOOLS_LICENSE_FILES = LICENSE
SPIRV_TOOLS_DEPENDENCIES = spirv-headers
SPIRV_TOOLS_INSTALL_STAGING = YES

SPIRV_TOOLS_CONF_OPTS = \
	-DSPIRV-Headers_SOURCE_DIR=$(STAGING_DIR)/usr \
	-DSPIRV_TOOLS_BUILD_STATIC=OFF \
	-DSPIRV_SKIP_TESTS=ON \
	-DSPIRV_WERROR=OFF

$(eval $(cmake-package))

HOST_SPIRV_TOOLS_CONF_OPTS = \
	-DSPIRV-Headers_SOURCE_DIR=$(HOST_DIR)/usr \
	-DSPIRV_TOOLS_BUILD_STATIC=OFF \
	-DSPIRV_SKIP_TESTS=ON \
	-DSPIRV_WERROR=OFF

HOST_SPIRV_TOOLS_DEPENDENCIES = host-spirv-headers

$(eval $(host-cmake-package))

else

# Prebuilt, published on REG-llvm-binaries under its own release tag,
# spirv-tools-$(SPIRV_TOOLS_VERSION).
#
# Keyed on SPIRV_TOOLS_VERSION alone - tag and filename both - because
# spirv-tools has no LLVM coupling whatsoever: its only dependency is
# spirv-headers, and it is versioned by the Vulkan SDK. An LLVM bump therefore
# leaves this release untouched, and the ~10 min/board it costs to build is not
# spent again.
SPIRV_TOOLS_SITE = https://github.com/REG-Linux/REG-llvm-binaries/releases/download/spirv-tools-$(SPIRV_TOOLS_VERSION)
SPIRV_TOOLS_SOURCE = reglinux-spirv-tools-target-$(SPIRV_TOOLS_VERSION)-$(REGLINUX_LLVM_CPU).tar.xz
SPIRV_TOOLS_DEPENDENCIES = spirv-headers host-spirv-tools
SPIRV_TOOLS_INSTALL_STAGING = YES

HOST_SPIRV_TOOLS_SITE = $(SPIRV_TOOLS_SITE)
HOST_SPIRV_TOOLS_SOURCE = reglinux-spirv-tools-host-$(SPIRV_TOOLS_VERSION)-$(REGLINUX_LLVM_CPU).tar.xz
HOST_SPIRV_TOOLS_DEPENDENCIES = host-spirv-headers


# The prebuilt tarball is per-CPU, so it cannot have a hash entry. Tell
# buildroot's check-hash to skip it by name (support/download/check-hash matches
# the basename against BR_NO_CHECK_HASH_FOR) instead of moving the .hash file
# aside around the download. The old PRE/POST_DOWNLOAD rename hooks were not
# failure-safe: a download error - a 404 for an unpublished asset, say - aborts
# between the two, leaving the .hash renamed to .hash.bak and the next build
# unable to find it.
BR_NO_CHECK_HASH_FOR += $(SPIRV_TOOLS_SOURCE) $(HOST_SPIRV_TOOLS_SOURCE)

define HOST_SPIRV_TOOLS_EXTRACT_CMDS
endef
# host/ only, never the staging half the bundle also carries under
# host/<tuple>/sysroot. Staging is the target package's job (see
# SPIRV_TOOLS_INSTALL_STAGING_CMDS below), and it is only there that the
# matching runtime .so also reaches TARGET_DIR. Unpacking it from here put
# SPIRV-Tools.pc in the sysroot of boards that never enabled the target package
# at all - lima-only cha among them - where mesa's -Dspirv-tools defaults to
# auto, found it, and linked libgallium against a library nothing installs. The
# board then boots to a black screen: every GL client dies with "Error loading
# shared library libSPIRV-Tools.so".
define HOST_SPIRV_TOOLS_INSTALL_CMDS
	tar -C $(HOST_DIR)/../ -xf $(HOST_SPIRV_TOOLS_DL_DIR)/$(HOST_SPIRV_TOOLS_SOURCE) \
		--exclude='host/*/sysroot' host
endef

# The bundle for this CPU was harvested on one representative board (cortex_a7
# means h3), so spirv-as and the SPIRV-Tools libraries carry that board's
# absolute RUNPATH and are unusable - and rejected by check-host-rpath -
# anywhere else. See REGLINUX_PREBUILT_HOST_FIX_RPATH in llvm-project.mk.
HOST_SPIRV_TOOLS_DEPENDENCIES += host-patchelf
define HOST_SPIRV_TOOLS_FIX_RPATH
	$(call REGLINUX_PREBUILT_HOST_FIX_RPATH,\
		$(HOST_SPIRV_TOOLS_DL_DIR)/$(HOST_SPIRV_TOOLS_SOURCE),$(HOST_DIR))
endef
HOST_SPIRV_TOOLS_POST_INSTALL_HOOKS += HOST_SPIRV_TOOLS_FIX_RPATH

define SPIRV_TOOLS_EXTRACT_CMDS
endef
define SPIRV_TOOLS_INSTALL_STAGING_CMDS
	mkdir -p $(STAGING_DIR)
	tar -C $(STAGING_DIR) --strip-components=1 -xf $(SPIRV_TOOLS_DL_DIR)/$(SPIRV_TOOLS_SOURCE) target/usr
endef
define SPIRV_TOOLS_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)
	tar -C $(TARGET_DIR)/../ -xf $(SPIRV_TOOLS_DL_DIR)/$(SPIRV_TOOLS_SOURCE) target
endef

$(eval $(generic-package))
$(eval $(host-generic-package))
endif
