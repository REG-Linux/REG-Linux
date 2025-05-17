################################################################################
#
# clang
#
################################################################################

CLANG_VERSION_MAJOR = $(LLVM_PROJECT_VERSION_MAJOR)
CLANG_VERSION = $(LLVM_PROJECT_VERSION)

ifeq ($(BR2_PACKAGE_LLVM_BUILD_FROM_SOURCE),y)

CLANG_SITE = $(LLVM_PROJECT_SITE)
CLANG_SOURCE = clang-$(CLANG_VERSION).src.tar.xz
CLANG_LICENSE = Apache-2.0 with exceptions
CLANG_LICENSE_FILES = LICENSE.TXT
CLANG_CPE_ID_VENDOR = llvm
CLANG_SUPPORTS_IN_SOURCE_BUILD = NO
CLANG_INSTALL_STAGING = YES

HOST_CLANG_DEPENDENCIES = host-llvm host-libxml2
CLANG_DEPENDENCIES = llvm host-clang

# This option is needed, otherwise multiple shared libs
# (libclangAST.so, libclangBasic.so, libclangFrontend.so, etc.) will
# be generated. As a final shared lib containing all these components
# (libclang.so) is also generated, this resulted in the following
# error when trying to use tools that use libclang:
# $ CommandLine Error: Option 'track-memory' registered more than once!
# $ LLVM ERROR: inconsistency in registered CommandLine options
# By setting BUILD_SHARED_LIBS to OFF, we generate multiple static
# libraries (the same way as host's clang build) and finally
# libclang.so to be installed on the target.
HOST_CLANG_CONF_OPTS += -DBUILD_SHARED_LIBS=OFF
CLANG_CONF_OPTS += -DBUILD_SHARED_LIBS=OFF

# Default is Debug build, which requires considerably more disk space
# and build time. Release build is selected for host and target
# because the linker can run out of memory in Debug mode.
HOST_CLANG_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release
CLANG_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release

CLANG_CONF_OPTS += -DCMAKE_CROSSCOMPILING=1

# We need to build tools because libclang is a tool
HOST_CLANG_CONF_OPTS += -DCLANG_BUILD_TOOLS=ON
CLANG_CONF_OPTS += -DCLANG_BUILD_TOOLS=ON

HOST_CLANG_CONF_OPTS += \
	-DCLANG_BUILD_EXAMPLES=OFF \
	-DCLANG_INCLUDE_DOCS=OFF \
	-DCLANG_INCLUDE_TESTS=OFF \
	-DLLVM_INCLUDE_TESTS=OFF

CLANG_CONF_OPTS += \
	-DCLANG_BUILD_EXAMPLES=OFF \
	-DCLANG_INCLUDE_DOCS=OFF \
	-DCLANG_INCLUDE_TESTS=OFF \
	-DLLVM_INCLUDE_TESTS=OFF

# batocera - add LLVM_COMMON_CMAKE_UTILS
HOST_CLANG_CONF_OPTS += -DLLVM_DIR=$(HOST_DIR)/lib/cmake/llvm \
	-DCLANG_DEFAULT_LINKER=$(TARGET_LD) \
	-DLLVM_COMMON_CMAKE_UTILS=$(HOST_DIR)/lib/cmake/llvm
CLANG_CONF_OPTS += -DLLVM_DIR=$(STAGING_DIR)/usr/lib/cmake/llvm \
	-DCMAKE_MODULE_PATH=$(HOST_DIR)/lib/cmake/llvm \
	-DCLANG_TABLEGEN:FILEPATH=$(HOST_DIR)/bin/clang-tblgen \
	-DLLVM_TABLEGEN_EXE:FILEPATH=$(HOST_DIR)/bin/llvm-tblgen

# Clang can't be used as compiler on the target since there are no
# development files (headers) and other build tools. So remove clang
# binaries and some other unnecessary files from target.
CLANG_FILES_TO_REMOVE = \
	/usr/bin/clang* \
	/usr/bin/c-index-test \
	/usr/bin/git-clang-format \
	/usr/bin/scan-build \
	/usr/bin/scan-view \
	/usr/libexec/c++-analyzer \
	/usr/libexec/ccc-analyzer \
	/usr/share/clang \
	/usr/share/opt-viewer \
	/usr/share/scan-build \
	/usr/share/scan-view \
	/usr/share/man/man1/scan-build.1 \
	/usr/lib/clang

define CLANG_CLEANUP_TARGET
	rm -rf $(addprefix $(TARGET_DIR),$(CLANG_FILES_TO_REMOVE))
endef

CLANG_POST_INSTALL_TARGET_HOOKS += CLANG_CLEANUP_TARGET

# clang-tblgen is not installed by default, however it is necessary
# for cross-compiling clang
define HOST_CLANG_INSTALL_CLANG_TBLGEN
	$(INSTALL) -D -m 0755 $(HOST_CLANG_BUILDDIR)/bin/clang-tblgen \
		$(HOST_DIR)/bin/clang-tblgen
endef
HOST_CLANG_POST_INSTALL_HOOKS = HOST_CLANG_INSTALL_CLANG_TBLGEN

# This option must be enabled to link libclang dynamically against libLLVM.so
HOST_CLANG_CONF_OPTS += -DLLVM_LINK_LLVM_DYLIB=ON
CLANG_CONF_OPTS += -DLLVM_LINK_LLVM_DYLIB=ON

# Prevent clang binaries from linking against LLVM static libs
HOST_CLANG_CONF_OPTS += -DLLVM_DYLIB_COMPONENTS=all
CLANG_CONF_OPTS += -DLLVM_DYLIB_COMPONENTS=all

# Help host-clang to find our external toolchain, use a relative path from the clang
# installation directory to the external toolchain installation directory in order to
# not hardcode the toolchain absolute path.
ifeq ($(BR2_TOOLCHAIN_EXTERNAL),y)
HOST_CLANG_CONF_OPTS += -DGCC_INSTALL_PREFIX:PATH=`realpath --relative-to=$(HOST_DIR)/bin/ $(TOOLCHAIN_EXTERNAL_INSTALL_DIR)`
endif

define HOST_CLANG_INSTALL_WRAPPER_AND_SIMPLE_SYMLINKS
	$(Q)cd $(HOST_DIR)/bin; \
	rm -f clang-$(CLANG_VERSION_MAJOR).br_real; \
	mv clang-$(CLANG_VERSION_MAJOR) clang-$(CLANG_VERSION_MAJOR).br_real; \
	ln -sf toolchain-wrapper-clang clang-$(CLANG_VERSION_MAJOR); \
	for i in clang clang++ clang-cl clang-cpp; do \
		ln -snf toolchain-wrapper-clang $$i; \
		ln -snf clang-$(CLANG_VERSION_MAJOR).br_real $$i.br_real; \
	done
endef

define HOST_CLANG_TOOLCHAIN_WRAPPER_BUILD
	$(HOSTCC) $(HOST_CFLAGS) $(TOOLCHAIN_WRAPPER_ARGS) \
		-s -Wl,--hash-style=$(TOOLCHAIN_WRAPPER_HASH_STYLE) \
		toolchain/toolchain-wrapper.c \
		-o $(@D)/toolchain-wrapper-clang
endef

define HOST_CLANG_TOOLCHAIN_WRAPPER_INSTALL
	$(INSTALL) -D -m 0755 $(@D)/toolchain-wrapper-clang \
		$(HOST_DIR)/bin/toolchain-wrapper-clang
endef

HOST_CLANG_TOOLCHAIN_WRAPPER_ARGS += -DBR_CROSS_PATH_SUFFIX='".br_real"'
HOST_CLANG_POST_BUILD_HOOKS += HOST_CLANG_TOOLCHAIN_WRAPPER_BUILD
HOST_CLANG_POST_INSTALL_HOOKS += HOST_CLANG_TOOLCHAIN_WRAPPER_INSTALL
HOST_CLANG_POST_INSTALL_HOOKS += HOST_CLANG_INSTALL_WRAPPER_AND_SIMPLE_SYMLINKS

$(eval $(cmake-package))
$(eval $(host-cmake-package))

else

# Download pre compiled files
REGLINUX_CLANG_ARCH = unknown
ifeq ($(BR2_arm),y)
ifeq ($(BR2_arm1176jzf_s),y)
    # bcm2835
    REGLINUX_CLANG_ARCH = armhf
else
    # h3
    REGLINUX_CLANG_ARCH = armv7
endif
else ifeq ($(BR2_aarch64),y)
ifeq ($(BR2_saphira),y)
    # Asahi Linux
    REGLINUX_CLANG_ARCH = asahi
else
    # h5, Cortex A53
    REGLINUX_CLANG_ARCH = aarch64
endif
else ifeq ($(BR2_RISCV_64),y)
# jh7110, RISC-V 64 (rv64gc, aka imafd)
REGLINUX_CLANG_ARCH = riscv64
else ifeq ($(BR2_x86_64),y)
# X86_64 architecture
REGLINUX_CLANG_ARCH = x86_64
endif

CLANG_SITE = https://github.com/REG-Linux/REG-llvm-binaries/releases/download/$(CLANG_VERSION)
CLANG_SOURCE = reglinux-clang-$(CLANG_VERSION)-$(REGLINUX_CLANG_ARCH).tar.xz
HOST_CLANG_DEPENDENCIES = host-libxml2

define DELETE_CLANG_HASH_IF_NOT_BUILD_FROM_SOURCE
	rm -f $(BR2_EXTERNAL)/buildroot/package/llvm-project/clang/*.hash -f $(BR2_EXTERNAL)/buildroot/package/llvm-project/clang/*.patch
endef

define DISABLE_CLANG_PATCHES_IF_NOT_BUILD_FROM_SOURCE
	$(foreach dir,$(call pkg-patches-dirs,$(PKG)),\
		mkdir -p $(dir)/tmp_disabled_patches ; mv -v $(dir)/*.patch $(dir)/tmp_disabled_patches/ ; \
	)
endef

define ENABLE_CLANG_PATCHES_IF_NOT_BUILD_FROM_SOURCE
	$(foreach dir,$(call pkg-patches-dirs,$(PKG)),\
		mv -v $(dir)/tmp_disabled_patches/* $(dir)/ ; rmdir $(dir)/tmp_disabled_patches ; \
	)
endef

CLANG_PRE_DOWNLOAD_HOOKS += DELETE_CLANG_HASH_IF_NOT_BUILD_FROM_SOURCE
CLANG_PRE_PATCH_HOOKS += DISABLE_CLANG_PATCHES_IF_NOT_BUILD_FROM_SOURCE
CLANG_POST_PATCH_HOOKS += ENABLE_CLANG_PATCHES_IF_NOT_BUILD_FROM_SOURCE

define CLANG_EXTRACT_CMDS
	# extract host folder
	tar -C $(HOST_DIR)/../ -xvf $(DL_DIR)/$(CLANG_DL_SUBDIR)/$(CLANG_SOURCE) host
endef

define CLANG_INSTALL_TARGET_CMDS
	# extract target folder
	tar -C $(TARGET_DIR)/../ -xvf $(DL_DIR)/$(CLANG_DL_SUBDIR)/$(CLANG_SOURCE) target
endef

$(eval $(generic-package))
endif

