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
	-DCMAKE_CLC_COMPILER_FORCED=ON \
	-DCMAKE_LLAsm_COMPILER_FORCED=ON \
	-DCMAKE_INSTALL_DATADIR="share" \
	-DCMAKE_FIND_ROOT_PATH="$(HOST_DIR)" \
	-DCMAKE_C_FLAGS="$(HOST_CFLAGS)" \
	-DCMAKE_CXX_FLAGS="$(HOST_CXXFLAGS)" \
	-DCMAKE_EXE_LINKER_FLAGS="$(HOST_LDFLAGS)" \
	-DCMAKE_SHARED_LINKER_FLAGS="$(HOST_LDFLAGS)" \
	-DCMAKE_MODULE_LINKER_FLAGS="$(HOST_LDFLAGS)" \
	-DCMAKE_C_COMPILER="$(CMAKE_HOST_C_COMPILER)" \
	-DCMAKE_CXX_COMPILER="$(CMAKE_HOST_CXX_COMPILER)" \
	-DLLVM_CONFIG="$(HOST_DIR)/bin/llvm-config"

# REG fixup host-libclc for host-mesa3d + prepare_builtins fixup
define HOST_LIBCLC_COPY_HOST_PREPARE_BUILTINS
	cp $(@D)/buildroot-build/prepare_builtins $(HOST_DIR)/usr/bin/
endef
HOST_LIBCLC_POST_BUILD_HOOKS += HOST_LIBCLC_COPY_HOST_PREPARE_BUILTINS

$(eval $(cmake-package))
$(eval $(host-cmake-package))

else

# Download pre compiled files
REGLINUX_LIBCLC_ARCH = unknown
ifeq ($(BR2_arm),y)
ifeq ($(BR2_arm1176jzf_s),y)
    # bcm2835
    REGLINUX_LIBCLC_ARCH = armhf
else
    # h3
    REGLINUX_LIBCLC_ARCH = armv7
endif
else ifeq ($(BR2_aarch64),y)
ifeq ($(BR2_saphira),y)
    # Asahi Linux
    REGLINUX_LIBCLC_ARCH = asahi
else
    # h5, Cortex A53
    REGLINUX_LIBCLC_ARCH = aarch64
endif
else ifeq ($(BR2_RISCV_64),y)
# jh7110, RISC-V 64 (rv64gc, aka imafd)
REGLINUX_LIBCLC_ARCH = riscv64
else ifeq ($(BR2_x86_64),y)
# X86_64 architecture
REGLINUX_LIBCLC_ARCH = x86_64
endif

LIBCLC_SITE = https://github.com/REG-Linux/REG-llvm-binaries/releases/download/$(LIBCLC_VERSION)
LIBCLC_SOURCE = reglinux-libclc-$(LIBCLC_VERSION)-$(REGLINUX_LIBCLC_ARCH).tar.xz
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

$(eval $(generic-package))
endif

