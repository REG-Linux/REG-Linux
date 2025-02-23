################################################################################
#
# spirv-tools
#
################################################################################
# reglinux - 1.4.304.0 needed to build spirv-llvm-translator
SPIRV_TOOLS_VERSION = 1.4.304.0
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
