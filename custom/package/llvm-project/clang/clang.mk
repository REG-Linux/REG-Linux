################################################################################
#
# clang
#
################################################################################

CLANG_VERSION_MAJOR = $(LLVM_PROJECT_VERSION_MAJOR)
CLANG_VERSION = $(LLVM_PROJECT_VERSION)

ifeq ($(BR2_PACKAGE_LLVM_BUILD_FROM_SOURCE),y)

CLANG_SITE = $(LLVM_PROJECT_SITE)
# reglinux - one shared llvm-project monolith, see llvm-project.mk
CLANG_SOURCE = $(LLVM_PROJECT_SOURCE)
CLANG_DL_SUBDIR = llvm-project
CLANG_SUBDIR = clang
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

# reglinux - add LLVM_COMMON_CMAKE_UTILS
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

# The prebuilt is two bundles owned by llvm.mk:
#   reglinux-llvm-host-<ver>-<cpu>.tar.xz   -> HOST_DIR    (host-llvm)
#   reglinux-llvm-target-<ver>-<cpu>.tar.xz -> TARGET_DIR  (llvm)
# Both carry clang alongside llvm, so there is nothing to fetch or install
# here - each variant just depends on the matching llvm variant, which is what
# lets a consumer ask for host tools without dragging the rootfs payload along.
#
# _SOURCE is set to the empty string rather than left unset: buildroot's
# `$(2)_SOURCE ?=` default would otherwise invent <pkg>-<version>.tar.gz, and an
# explicitly-empty value still counts as defined, so download and extract both
# become no-ops.
CLANG_SOURCE =
CLANG_DEPENDENCIES = llvm
HOST_CLANG_SOURCE =
HOST_CLANG_DEPENDENCIES = host-llvm

# Nothing is extracted on this path, but buildroot still runs the patch step and
# still scans for patches - pkg-patches-dirs draws from both $(CLANG_PKGDIR) and
# $(BR2_GLOBAL_PATCH_DIR)/clang, so there is no single switch to turn it off.
# clang has three (two here, one in board/patches/clang) and they all fail with
# "No file to patch" against the empty build directory. Move them aside for the
# duration, exactly as llvm.mk does.
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

CLANG_PRE_PATCH_HOOKS += DISABLE_CLANG_PATCHES_IF_NOT_BUILD_FROM_SOURCE
CLANG_POST_PATCH_HOOKS += ENABLE_CLANG_PATCHES_IF_NOT_BUILD_FROM_SOURCE
HOST_CLANG_PRE_PATCH_HOOKS += DISABLE_CLANG_PATCHES_IF_NOT_BUILD_FROM_SOURCE
HOST_CLANG_POST_PATCH_HOOKS += ENABLE_CLANG_PATCHES_IF_NOT_BUILD_FROM_SOURCE

# Both variants patch the SAME shared directories (package/llvm-project/clang/ and board/patches/clang/),
# outside the per-package dirs, so under PARALLEL_BUILD=y their PRE hooks
# race: whichever patches first moves the *.patch files aside and the
# other's mv dies with "cannot stat ... No such file or directory",
# failing .stamp_patched. Guarding the mv would only hide it - the first
# package's POST hook would then restore the patches while the second is
# still patching, and a source patch would land on a prebuilt tarball.
# Order the two patch steps instead; buildroot turns this into an
# order-only dependency on host-clang-patch (pkg-generic.mk), so each
# move-aside/restore pair runs to completion before the next begins.
CLANG_PATCH_DEPENDENCIES = host-clang

$(eval $(generic-package))
$(eval $(host-generic-package))
endif
