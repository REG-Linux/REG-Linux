################################################################################
#
# vulkan-headers
#
################################################################################
# reglinux - bump
VULKAN_HEADERS_VERSION = 1.4.357.0
VULKAN_HEADERS_SITE = $(call github,KhronosGroup,Vulkan-Headers,vulkan-sdk-$(VULKAN_HEADERS_VERSION))
VULKAN_HEADERS_LICENSE = Apache-2.0 OR MIT
VULKAN_HEADERS_LICENSE_FILES = LICENSE.md LICENSES/Apache-2.0.txt LICENSES/MIT.txt
VULKAN_HEADERS_INSTALL_STAGING = YES

# reglinux
ifeq ($(BR2_PACKAGE_MESA3D),y)
VULKAN_HEADERS_DEPENDENCIES += mesa3d
endif

$(eval $(cmake-package))
