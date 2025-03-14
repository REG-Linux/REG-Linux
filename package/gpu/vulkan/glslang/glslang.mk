################################################################################
#
# glslang
#
################################################################################

GLSLANG_VERSION = 15.1.0
GLSLANG_SITE =  https://github.com/KhronosGroup/glslang
GLSLANG_SITE_METHOD=git
GLSLANG_DEPENDENCIES = spirv-tools

GLSLANG_INSTALL_STAGING = YES
GLSLANG_SUPPORTS_IN_SOURCE_BUILD = NO

ifeq ($(BR2_PACKAGE_REGLINUX_VULKAN),y)
GLSLANG_DEPENDENCIES += vulkan-headers vulkan-loader
endif

ifeq ($(BR2_PACKAGE_MESA3D),y)
GLSLANG_DEPENDENCIES += mesa3d
endif

GLSLANG_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release
GLSLANG_CONF_OPTS += -DBUILD_EXTERNAL=OFF
GLSLANG_CONF_OPTS += -DALLOW_EXTERNAL_SPIRV_TOOLS=1
GLSLANG_CONF_OPTS += -DSPIRV-Tools-opt_DIR=$(STAGING_DIR)/usr/lib/cmake/SPIRV-Tools-opt
GLSLANG_CONF_OPTS += -DSPIRV-Tools_DIR=$(STAGING_DIR)/usr/lib/cmake/SPIRV-Tools
GLSLANG_CONF_OPTS += -DGLSLANG_TESTS=OFF
GLSLANG_CONF_OPTS += -DENABLE_GLSLANG_BINARIES=OFF

GLSLANG_CONF_ENV += LDFLAGS="-lpthread -ldl"

$(eval $(cmake-package))

HOST_GLSLANG_DEPENDENCIES = host-spirv-tools

HOST_GLSLANG_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release
HOST_GLSLANG_CONF_OPTS += -DENABLE_OPT=0

$(eval $(host-cmake-package))
