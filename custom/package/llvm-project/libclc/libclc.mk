################################################################################
#
# libclc
#
################################################################################
# REG remove 0001-support-out-of-tree-build.patch
LIBCLC_VERSION = $(LLVM_PROJECT_VERSION)

ifeq ($(BR2_PACKAGE_LLVM_BUILD_FROM_SOURCE),y)

LIBCLC_SITE = $(LLVM_PROJECT_SITE)
LIBCLC_SOURCE = libclc-$(LIBCLC_VERSION).src.tar.xz
LIBCLC_LICENSE = Apache-2.0 with exceptions or MIT
LIBCLC_LICENSE_FILES = LICENSE.TXT
LIBCLC_SUPPORTS_IN_SOURCE_BUILD = NO
HOST_LIBCLC_SUPPORTS_IN_SOURCE_BUILD = NO

# REG we need host-libclc for prepare_builtins
LIBCLC_DEPENDENCIES = host-clang host-llvm host-spirv-llvm-translator host-libclc
# REG add host package for host-mesa3d
HOST_LIBCLC_DEPENDENCIES = host-clang host-llvm host-spirv-llvm-translator
LIBCLC_INSTALL_STAGING = YES

# CMAKE_*_COMPILER_FORCED=ON skips testing the tools and assumes
# llvm-config provided values
#
# CMAKE_*_COMPILER has to be set to the host compiler to build a host
# 'prepare_builtins' tool used during the build process
#
# The headers are installed in /usr/share and not /usr/include,
# because they are needed at runtime on the target to build the OpenCL
# kernels.
LIBCLC_CONF_OPTS = \
	-DCMAKE_SYSROOT="" \
	-DCMAKE_C_COMPILER_FORCED=ON \
	-DCMAKE_CXX_COMPILER_FORCED=ON \
	-DCMAKE_INSTALL_DATADIR="share" \
	-DCMAKE_FIND_ROOT_PATH="$(HOST_DIR)" \
	-DCMAKE_C_FLAGS="$(HOST_CFLAGS)" \
	-DCMAKE_CXX_FLAGS="$(HOST_CXXFLAGS)" \
	-DCMAKE_EXE_LINKER_FLAGS="$(HOST_LDFLAGS)" \
	-DCMAKE_SHARED_LINKER_FLAGS="$(HOST_LDFLAGS)" \
	-DCMAKE_MODULE_LINKER_FLAGS="$(HOST_LDFLAGS)" \
	-DCMAKE_C_COMPILER="$(CMAKE_HOST_C_COMPILER)" \
	-DCMAKE_CXX_COMPILER="$(CMAKE_HOST_CXX_COMPILER)" \
	-DLLVM_CMAKE_DIR="$(HOST_DIR)/lib/cmake/llvm" \
	-DLIBCLC_CUSTOM_LLVM_TOOLS_BINARY_DIR="$(HOST_DIR)/bin"

ifeq ($(BR2_arm)$(BR2_aarch64),y)
HOST_LIBCLC_CONF_OPTS = \
	-DLIBCLC_TARGETS_TO_BUILD=""
LIBCLC_CONF_OPTS += -DLIBCLC_TARGETS_TO_BUILD=""
endif

define APPLY_PATCH_BEFORE_LLVM_BUILD_FROM_SOURCE
    patch "$(@D)/CMakeLists.txt" < "$(BR2_EXTERNAL)/buildroot/package/llvm-project/libclc/patch-to-fix-prepare_builtins-not-found
endef

LIBCLC_PRE_CONFIGURE_HOOKS += APPLY_PATCH_BEFORE_LLVM_BUILD_FROM_SOURCE

$(eval $(cmake-package))
$(eval $(host-cmake-package))

else

# Download pre compiled files
REGLINUX_LIBCLC_CPU = unknown
ifeq ($(BR2_arm1176jzf_s),y)
	REGLINUX_LIBCLC_CPU = arm1176jzf_s
else ifeq ($(BR2_cortex_a7),y)
	REGLINUX_LIBCLC_CPU = cortex_a7
else ifeq ($(BR2_cortex_a9),y)
	REGLINUX_LIBCLC_CPU = cortex_a9
else ifeq ($(BR2_cortex_a15_a7),y)
	REGLINUX_LIBCLC_CPU = cortex_a15_a7
else ifeq ($(BR2_cortex_a17),y)
	REGLINUX_LIBCLC_CPU = cortex_a17
else ifeq ($(BR2_cortex_a35),y)
	REGLINUX_LIBCLC_CPU = cortex_a35
else ifeq ($(BR2_cortex_a53),y)
	REGLINUX_LIBCLC_CPU = cortex_a53
else ifeq ($(BR2_jz4770),y)
	REGLINUX_LIBCLC_CPU = jz4770
else ifeq ($(BR2_cortex_a55),y)
	REGLINUX_LIBCLC_CPU = cortex_a55
else ifeq ($(BR2_cortex_a72),y)
	REGLINUX_LIBCLC_CPU = cortex_a72
else ifeq ($(BR2_cortex_a72_a53),y)
	REGLINUX_LIBCLC_CPU = cortex_a72_a53
else ifeq ($(BR2_cortex_a73_a53),y)
	REGLINUX_LIBCLC_CPU = cortex_a73_a53
else ifeq ($(BR2_cortex_a75_a55),y)
	REGLINUX_LIBCLC_CPU = cortex_a75_a55
else ifeq ($(BR2_cortex_a76),y)
	REGLINUX_LIBCLC_CPU = cortex_a76
else ifeq ($(BR2_cortex_a76_a55),y)
	REGLINUX_LIBCLC_CPU = cortex_a76_a55
else ifeq ($(BR2_ARM_CPU_ARMV9A),y) # TODO
	REGLINUX_LIBCLC_CPU = cortex_a76_a55
else ifeq ($(BR2_riscv),y)
	REGLINUX_LIBCLC_CPU = riscv
else ifeq ($(BR2_saphira),y)
	REGLINUX_LIBCLC_CPU = saphira
else ifeq ($(BR2_x86_64),y)
	REGLINUX_LIBCLC_CPU = x86_64
else ifeq ($(BR2_x86_64_v3),y)
	REGLINUX_LIBCLC_CPU = x86_64_v3
endif

LIBCLC_SITE = https://github.com/REG-Linux/REG-llvm-binaries/releases/download/$(LIBCLC_VERSION)
LIBCLC_SOURCE = reglinux-libclc-$(LIBCLC_VERSION)-$(REGLINUX_LIBCLC_CPU).tar.xz
LIBCLC_DEPENDENCIES = host-spirv-llvm-translator

define RENAME_LIBCLC_HASH_IF_NOT_BUILD_FROM_SOURCE
	mv $(BR2_EXTERNAL)/buildroot/package/llvm-project/libclc/libclc.hash $(BR2_EXTERNAL)/buildroot/package/llvm-project/libclc/libclc.hash.bak || :
endef

define RESTORE_LIBCLC_HASH_IF_NOT_BUILD_FROM_SOURCE
	mv $(BR2_EXTERNAL)/buildroot/package/llvm-project/libclc/libclc.hash.bak $(BR2_EXTERNAL)/buildroot/package/llvm-project/libclc/libclc.hash || :
endef

LIBCLC_PRE_DOWNLOAD_HOOKS += RENAME_LIBCLC_HASH_IF_NOT_BUILD_FROM_SOURCE
LIBCLC_POST_DOWNLOAD_HOOKS += RESTORE_LIBCLC_HASH_IF_NOT_BUILD_FROM_SOURCE

define LIBCLC_EXTRACT_CMDS
	# extract host folder
	tar -C $(HOST_DIR)/../ -xvf $(DL_DIR)/$(LIBCLC_DL_SUBDIR)/$(LIBCLC_SOURCE) host
endef

define LIBCLC_INSTALL_TARGET_CMDS
	# extract target folder
	tar -C $(TARGET_DIR)/../ -xvf $(DL_DIR)/$(LIBCLC_DL_SUBDIR)/$(LIBCLC_SOURCE) target
endef

define DELETE_LIBCLC_UNUSED_TARGETS
	# remove amdgcn, r600, nvp targets
	rm -Rf $(TARGET_DIR)/usr/share/clc/*amdgcn*
	rm -Rf $(TARGET_DIR)/usr/share/clc/*r600*
	rm -Rf $(TARGET_DIR)/usr/share/clc/*nvptx*
endef

ifeq ($(BR2_arm)$(BR2_aarch64),y)
LIBCLC_POST_INSTALL_TARGET_HOOKS += DELETE_LIBCLC_UNUSED_TARGETS
endif

$(eval $(generic-package))
endif
