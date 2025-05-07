################################################################################
#
# spirv-llvm-translator
#
################################################################################

# Generate version string using:
#   git describe --tags --match 'v18*' --abbrev=40 origin/llvm_release_180
# reglinux - 19.1.4 update
SPIRV_LLVM_TRANSLATOR_VERSION = v19.1.4
SPIRV_LLVM_TRANSLATOR_SITE = $(call github,KhronosGroup,SPIRV-LLVM-Translator,$(SPIRV_LLVM_TRANSLATOR_VERSION))
SPIRV_LLVM_TRANSLATOR_LICENSE = NCSA
SPIRV_LLVM_TRANSLATOR_LICENSE_FILES = LICENSE.TXT

# reglinux we need target package for some mesa targets
SPIRV_LLVM_TRANSLATOR_INSTALL_STAGING = YES
SPIRV_LLVM_TRANSLATOR_DEPENDENCIES = host-spirv-llvm-translator clang llvm spirv-headers
SPIRV_LLVM_TRANSLATOR_CONF_OPTS = \
	-DLLVM_BUILD_TOOLS=ON \
	-DLLVM_DIR=$(STAGING_DIR)/lib/cmake/llvm \
	-DLLVM_SPIRV_BUILD_EXTERNAL=YES \
	-DLLVM_SPIRV_INCLUDE_TESTS=OFF \
	-DLLVM_EXTERNAL_PROJECTS="SPIRV-Headers" \
	-DLLVM_EXTERNAL_SPIRV_HEADERS_SOURCE_DIR=$(STAGING_DIR)/include
$(eval $(cmake-package))

# reglinux define both host and targets
ifeq ($(BR2_PACKAGE_REGLINUX_LLVM_BUILD_FROM_SOURCE),y)
HOST_SPIRV_LLVM_TRANSLATOR_DEPENDENCIES = host-clang host-llvm host-spirv-headers
else
HOST_SPIRV_LLVM_TRANSLATOR_DEPENDENCIES += reglinux-llvm host-spirv-headers
endif
HOST_SPIRV_LLVM_TRANSLATOR_CONF_OPTS = \
	-DLLVM_BUILD_TOOLS=ON \
	-DLLVM_DIR=$(HOST_DIR)/lib/cmake/llvm \
	-DLLVM_SPIRV_BUILD_EXTERNAL=YES \
	-DLLVM_SPIRV_INCLUDE_TESTS=OFF \
	-DLLVM_EXTERNAL_PROJECTS="SPIRV-Headers" \
	-DLLVM_EXTERNAL_SPIRV_HEADERS_SOURCE_DIR=$(HOST_DIR)/include
$(eval $(host-cmake-package))

