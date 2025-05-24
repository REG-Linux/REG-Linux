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
SPIRV_LLVM_TRANSLATOR_DEPENDENCIES = host-spirv-llvm-translator llvm clang spirv-headers
SPIRV_LLVM_TRANSLATOR_CONF_OPTS = \
	-DLLVM_BUILD_TOOLS=ON \
	-DLLVM_DIR=$(STAGING_DIR)/lib/cmake/llvm \
	-DLLVM_SPIRV_BUILD_EXTERNAL=YES \
	-DLLVM_SPIRV_INCLUDE_TESTS=OFF \
	-DLLVM_EXTERNAL_PROJECTS="SPIRV-Headers" \
	-DLLVM_EXTERNAL_SPIRV_HEADERS_SOURCE_DIR=$(STAGING_DIR)/include
$(eval $(cmake-package))

# reglinux define both host and targets
HOST_SPIRV_LLVM_TRANSLATOR_DEPENDENCIES = llvm clang host-spirv-headers
HOST_SPIRV_LLVM_TRANSLATOR_CONF_OPTS = \
	-DLLVM_BUILD_TOOLS=ON \
	-DLLVM_DIR=$(HOST_DIR)/lib/cmake/llvm \
	-DLLVM_SPIRV_BUILD_EXTERNAL=YES \
	-DLLVM_SPIRV_INCLUDE_TESTS=OFF \
	-DLLVM_EXTERNAL_PROJECTS="SPIRV-Headers" \
	-DLLVM_EXTERNAL_SPIRV_HEADERS_SOURCE_DIR=$(HOST_DIR)/include

# reglinux fix for prebuilt llvm/clang
#HOST_SPIRV_LLVM_TRANSLATOR_CONF_OPTS += -DCMAKE_INSTALL_RPATH="$(HOST_DIR)/lib"
# -DCMAKE_INSTALL_RPATH_USE_LINK_PATH=TRUE
HOST_SPIRV_LLVM_TRANSLATOR_DEPENDENCIES += host-patchelf
define HOST_SPIRV_LLVM_TRANSLATOR_FIX_RPATH
    for f in $(HOST_DIR)/bin/llvm-* $(HOST_DIR)/bin/*ll*; do \
        $(HOST_DIR)/bin/patchelf --set-rpath '$$ORIGIN/../lib' $$f || true; \
    done
    $(HOST_DIR)/bin/patchelf --set-rpath '$$ORIGIN/../lib' $(HOST_DIR)/bin/obj2yaml || true;
    $(HOST_DIR)/bin/patchelf --set-rpath '$$ORIGIN/../lib' $(HOST_DIR)/bin/yaml2obj || true;
    $(HOST_DIR)/bin/patchelf --set-rpath '$$ORIGIN/../lib' $(HOST_DIR)/bin/opt || true;
    $(HOST_DIR)/bin/patchelf --set-rpath '$$ORIGIN/../lib' $(HOST_DIR)/bin/sancov || true;
    $(HOST_DIR)/bin/patchelf --set-rpath '$$ORIGIN/../lib' $(HOST_DIR)/bin/verify-uselistorder || true;
    $(HOST_DIR)/bin/patchelf --set-rpath '$$ORIGIN/../lib' $(HOST_DIR)/bin/dsymutil || true;
    $(HOST_DIR)/bin/patchelf --set-rpath '$$ORIGIN/../lib' $(HOST_DIR)/bin/sanstats || true;
    $(HOST_DIR)/bin/patchelf --set-rpath '$$ORIGIN/../lib' $(HOST_DIR)/bin/reduce-chunk-list || true;
    $(HOST_DIR)/bin/patchelf --set-rpath '$$ORIGIN/../lib' $(HOST_DIR)/bin/bugpoint || true;
endef

HOST_SPIRV_LLVM_TRANSLATOR_POST_INSTALL_HOOKS += HOST_SPIRV_LLVM_TRANSLATOR_FIX_RPATH

$(eval $(host-cmake-package))

