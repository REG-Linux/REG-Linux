################################################################################
#
# shaderc
#
################################################################################
# Note: shaderc patch required from:
# https://github.com/PCSX2/pcsx2/blob/master/.github/workflows/scripts/common/shaderc-changes.patch
SHADERC_VERSION = v2025.3
SHADERC_SITE = $(call github,google,shaderc,$(SHADERC_VERSION))
SHADERC_LICENSE = Apache License v2
SHADERC_LICENSE_FILES = LICENSE
SHADERC_DEPENDENCIES = glslang spirv-headers host-spirv-tools spirv-tools
SHADERC_SUPPORTS_IN_SOURCE_BUILD = NO
SHADERC_INSTALL_STAGING = YES

SHADERC_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release
SHADERC_CONF_OPTS += -DSHADERC_SKIP_TESTS=ON
SHADERC_CONF_OPTS += -DSHADERC_SKIP_EXAMPLES=ON

# The PCSX2-derived patches vendor glslang/SPIRV-Tools and skip installing them,
# so they must link statically into libshaderc_shared.so.1. Buildroot's cmake
# infra forces BUILD_SHARED_LIBS=ON, which instead leaves a DT_NEEDED on an
# uninstalled libglslang.so.15/libSPIRV.so.15. CONF_OPTS come last, so this wins.
SHADERC_CONF_OPTS += -DBUILD_SHARED_LIBS=OFF

define SHADERC_SYNC_DEPS
	cd $(@D) && PATH=$(BR_PATH) ./utils/git-sync-deps
endef

SHADERC_PRE_CONFIGURE_HOOKS += SHADERC_SYNC_DEPS

$(eval $(cmake-package))

HOST_SHADERC_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release
HOST_SHADERC_CONF_OPTS += -DSHADERC_SKIP_TESTS=ON
HOST_SHADERC_CONF_OPTS += -DSHADERC_SKIP_EXAMPLES=ON
HOST_SHADERC_CONF_OPTS += -DBUILD_SHARED_LIBS=OFF

HOST_SHADERC_PRE_CONFIGURE_HOOKS += SHADERC_SYNC_DEPS

$(eval $(host-cmake-package))
