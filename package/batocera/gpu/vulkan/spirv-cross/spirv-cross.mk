################################################################################
#
# spirv-cross
#
################################################################################
# Version: Releaes on Dec 12, 2024
SPIRV_CROSS_VERSION = vulkan-sdk-1.4.304.0
SPIRV_CROSS_SITE = https://github.com/KhronosGroup/SPIRV-Cross
SPIRV_CROSS_GIT_SUBMODULES=YES
SPIRV_CROSS_SITE_METHOD=git

SPIRV_CROSS_DEPENDENCIES =

ifeq ($(BR2_PACKAGE_REGLINUX_VULKAN),y)
SPIRV_CROSS_DEPENDENCIES += vulkan-headers vulkan-loader
endif

SPIRV_CROSS_INSTALL_STAGING = YES
SPIRV_CROSS_SUPPORTS_IN_SOURCE_BUILD = NO

SPIRV_CROSS_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release
SPIRV_CROSS_CONF_OPTS += -DSPIRV_CROSS_SHARED=ON
SPIRV_CROSS_CONF_ENV += LDFLAGS="--lpthread -ldl"

# Terrible temporary workaround for rpi4
SPIRV_CROSS_INSTALL_ARCH = $(BR2_ARCH)
ifeq ($(ARCH),arm)
SPIRV_CROSS_INSTALL_ARCH = armv8l
endif

ifeq ($(BR2_PACKAGE_MESA3D),y)
SPIRV_CROSS_DEPENDENCIES += mesa3d
endif

$(eval $(cmake-package))
