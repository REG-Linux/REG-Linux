################################################################################
#
# Vulkan VOLK
#
################################################################################
VULKAN_VOLK_VERSION = vulkan-sdk-1.3.280.0
VULKAN_VOLK_SITE = https://github.com/zeux/volk
VULKAN_VOLK_SITE_METHOD=git
VULKAN_VOLK_GIT_SUBMODULES = YES
VULKAN_VOLK_LICENSE = Apache License 2.0
VULKAN_VOLK_DEPENDENCIES =

VULKAN_VOLK_SUPPORTS_IN_SOURCE_BUILD = NO

VULKAN_VOLK_INSTALL_STAGING = YES

VULKAN_VOLK_CONF_OPTS  = -DCMAKE_BUILD_TYPE=Release
VULKAN_VOLK_CONF_OPTS += -DBUILD_SHARED_LIBS=FALSE
VULKAN_VOLK_CONF_OPTS += -DVOLK_INSTALL=ON

VULKAN_VOLK_CONF_ENV += LDFLAGS=-lpthread

#define VULKAN_VOLK_GIT_SYNC_DEPS
#	cd $(@D) && ./utils/git-sync-deps
#endef

#VULKAN_VOLK_PRE_CONFIGURE_HOOKS += VULKAN_VOLK_GIT_SYNC_DEPS

$(eval $(cmake-package))
