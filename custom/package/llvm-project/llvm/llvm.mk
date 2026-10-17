################################################################################
#
# llvm
#
################################################################################

LLVM_VERSION = $(LLVM_PROJECT_VERSION)

ifeq ($(BR2_PACKAGE_LLVM_BUILD_FROM_SOURCE),y)

LLVM_SITE = $(LLVM_PROJECT_SITE)
# reglinux - one shared llvm-project monolith, see llvm-project.mk
LLVM_SOURCE = $(LLVM_PROJECT_SOURCE)
LLVM_DL_SUBDIR = llvm-project
LLVM_SUBDIR = llvm
LLVM_LICENSE = Apache-2.0 with exceptions
LLVM_LICENSE_FILES = LICENSE.TXT
LLVM_CPE_ID_VENDOR = llvm
LLVM_SUPPORTS_IN_SOURCE_BUILD = NO
LLVM_INSTALL_STAGING = YES

HOST_LLVM_DEPENDENCIES = host-python3 host-llvm-cmake
LLVM_DEPENDENCIES = host-llvm

# Path to cmake modules from host-llvm-cmake
HOST_LLVM_CONF_OPTS += -DCMAKE_MODULE_PATH=$(HOST_DIR)/lib/cmake/llvm
# reglinux add LLVM_COMMON_CMAKE_UTILS
HOST_LLVM_CONF_OPTS += -DLLVM_COMMON_CMAKE_UTILS=$(HOST_DIR)/lib/cmake/llvm
LLVM_CONF_OPTS += -DCMAKE_MODULE_PATH=$(HOST_DIR)/lib/cmake/llvm
LLVM_CONF_OPTS += -DLLVM_COMMON_CMAKE_UTILS=$(HOST_DIR)/lib/cmake/llvm

# Don't build clang libcxx libcxxabi lldb compiler-rt lld polly as llvm subprojects
# This flag assumes that projects are checked out side-by-side and not nested
HOST_LLVM_CONF_OPTS += -DLLVM_ENABLE_PROJECTS=""
LLVM_CONF_OPTS += -DLLVM_ENABLE_PROJECTS=""

HOST_LLVM_CONF_OPTS += -DLLVM_CCACHE_BUILD=$(if $(BR2_CCACHE),ON,OFF)
LLVM_CONF_OPTS += -DLLVM_CCACHE_BUILD=$(if $(BR2_CCACHE),ON,OFF)

# This option prevents AddLLVM.cmake from adding $ORIGIN/../lib to
# binaries. Otherwise, llvm-config (host variant installed in STAGING)
# will try to use target's libc.
HOST_LLVM_CONF_OPTS += -DCMAKE_INSTALL_RPATH="$(HOST_DIR)/lib"

# Get target architecture
LLVM_TARGET_ARCH = $(call qstrip,$(BR2_PACKAGE_LLVM_TARGET_ARCH))

# Build backend for target architecture. This include backends like
# AMDGPU. We need to special case RISCV.
ifneq ($(filter riscv%,$(LLVM_TARGET_ARCH)),)
LLVM_TARGETS_TO_BUILD = RISCV
else
LLVM_TARGETS_TO_BUILD = $(LLVM_TARGET_ARCH)
endif
HOST_LLVM_CONF_OPTS += -DLLVM_TARGETS_TO_BUILD="$(subst $(space),;,$(LLVM_TARGETS_TO_BUILD))"
LLVM_CONF_OPTS += -DLLVM_TARGETS_TO_BUILD="$(subst $(space),;,$(LLVM_TARGETS_TO_BUILD))"

# LLVM target to use for native code generation. This is required for JIT generation.
# It must be set to LLVM_TARGET_ARCH for host and target, otherwise we get
# "No available targets are compatible for this triple" with llvmpipe when host
# and target architectures are different.
HOST_LLVM_CONF_OPTS += -DLLVM_TARGET_ARCH=$(LLVM_TARGET_ARCH)
LLVM_CONF_OPTS += -DLLVM_TARGET_ARCH=$(LLVM_TARGET_ARCH)

# Build AMDGPU backend
# We need to build AMDGPU backend for both host and target because
# llvm-config --targets built (host variant installed in STAGING) will
# output only $(LLVM_TARGET_ARCH) if not, and mesa3d won't build as
# it thinks AMDGPU backend is not installed on the target.
ifeq ($(BR2_PACKAGE_LLVM_AMDGPU),y)
LLVM_TARGETS_TO_BUILD += AMDGPU
endif

# Build BPF backend
ifeq ($(BR2_PACKAGE_LLVM_BPF),y)
LLVM_TARGETS_TO_BUILD += BPF
endif

# Use native llvm-tblgen from host-llvm (needed for cross-compilation)
LLVM_CONF_OPTS += -DLLVM_TABLEGEN=$(HOST_DIR)/bin/llvm-tblgen

# Use native llvm-config from host-llvm (needed for cross-compilation)
LLVM_CONF_OPTS += -DLLVM_CONFIG_PATH=$(HOST_DIR)/bin/llvm-config

# BUILD_SHARED_LIBS has a misleading name. It is in fact an option for
# LLVM developers to build all LLVM libraries as separate shared libraries.
# For normal use of LLVM, it is recommended to build a single
# shared library, which is achieved by BUILD_SHARED_LIBS=OFF and
# LLVM_BUILD_LLVM_DYLIB=ON.
HOST_LLVM_CONF_OPTS += -DBUILD_SHARED_LIBS=OFF
LLVM_CONF_OPTS += -DBUILD_SHARED_LIBS=OFF

# Generate libLLVM.so. This library contains a default set of LLVM components
# that can be overwritten with "LLVM_DYLIB_COMPONENTS". The default contains
# most of LLVM and is defined in "tools/llvm-shlib/CMakelists.txt".
HOST_LLVM_CONF_OPTS += -DLLVM_BUILD_LLVM_DYLIB=ON
LLVM_CONF_OPTS += -DLLVM_BUILD_LLVM_DYLIB=ON

# LLVM_BUILD_LLVM_DYLIB to ON. We need to enable this option for the
# host as llvm-config for the host will be used in STAGING_DIR by packages
# linking against libLLVM and if this option is not selected, then llvm-config
# does not work properly. For example, it assumes that LLVM is built statically
# and cannot find libLLVM.so.
HOST_LLVM_CONF_OPTS += -DLLVM_LINK_LLVM_DYLIB=ON
LLVM_CONF_OPTS += -DLLVM_LINK_LLVM_DYLIB=ON

LLVM_CONF_OPTS += -DCMAKE_CROSSCOMPILING=1

# Disabled for the host since no host-libedit.
# Fall back to "Simple fgets-based implementation" of llvm line editor.
HOST_LLVM_CONF_OPTS += -DLLVM_ENABLE_LIBEDIT=OFF
LLVM_CONF_OPTS += -DLLVM_ENABLE_LIBEDIT=OFF

# We want to install llvm libraries and modules.
HOST_LLVM_CONF_OPTS += -DLLVM_INSTALL_TOOLCHAIN_ONLY=OFF
LLVM_CONF_OPTS += -DLLVM_INSTALL_TOOLCHAIN_ONLY=OFF

# We build from a release archive without vcs files.
HOST_LLVM_CONF_OPTS += -DLLVM_APPEND_VC_REV=OFF
LLVM_CONF_OPTS += -DLLVM_APPEND_VC_REV=OFF

# No backtrace package in Buildroot.
# https://documentation.backtrace.io
HOST_LLVM_CONF_OPTS += -DLLVM_ENABLE_BACKTRACES=OFF
LLVM_CONF_OPTS += -DLLVM_ENABLE_BACKTRACES=OFF

# Enable signal handlers overrides support.
HOST_LLVM_CONF_OPTS += -DENABLE_CRASH_OVERRIDES=ON
LLVM_CONF_OPTS += -DENABLE_CRASH_OVERRIDES=ON

# Disable ffi for now.
HOST_LLVM_CONF_OPTS += -DLLVM_ENABLE_FFI=OFF
LLVM_CONF_OPTS += -DLLVM_ENABLE_FFI=OFF

# Disable terminfo database (needs ncurses libtinfo.so)
HOST_LLVM_CONF_OPTS += -DLLVM_ENABLE_TERMINFO=OFF
LLVM_CONF_OPTS += -DLLVM_ENABLE_TERMINFO=OFF

# Enable thread support
HOST_LLVM_CONF_OPTS += -DLLVM_ENABLE_THREADS=ON
LLVM_CONF_OPTS += -DLLVM_ENABLE_THREADS=ON

# Enable optional host-zlib support for LLVM Machine Code (llvm-mc) to add
# compression/uncompression capabilities.
# Not needed on the target.
HOST_LLVM_CONF_OPTS += -DLLVM_ENABLE_ZLIB=ON
HOST_LLVM_DEPENDENCIES += host-zlib
LLVM_CONF_OPTS += -DLLVM_ENABLE_ZLIB=OFF

# libxml2 can be disabled as it is used for LLVM Windows builds where COFF
# files include manifest info
HOST_LLVM_CONF_OPTS += -DLLVM_ENABLE_LIBXML2=OFF
LLVM_CONF_OPTS += -DLLVM_ENABLE_LIBXML2=OFF

# Disable optional Z3Prover since there is no such package in Buildroot.
HOST_LLVM_CONF_OPTS += -DLLVM_ENABLE_Z3_SOLVER=OFF
LLVM_CONF_OPTS += -DLLVM_ENABLE_Z3_SOLVER=OFF

# We don't use llvm for static only build, so enable PIC
HOST_LLVM_CONF_OPTS += -DLLVM_ENABLE_PIC=ON
LLVM_CONF_OPTS += -DLLVM_ENABLE_PIC=ON

# Default is Debug build, which requires considerably more disk space and
# build time. Release build is selected for host and target because the linker
# can run out of memory in Debug mode.
HOST_LLVM_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release
LLVM_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release

# Compile llvm with the C++14 (ISO C++ 2014 standard).
HOST_LLVM_CONF_OPTS += -DCMAKE_CXX_STANDARD=14
LLVM_CONF_OPTS += -DCMAKE_CXX_STANDARD=14

# Disabled, requires sys/ndir.h header
# Disable debug in module
HOST_LLVM_CONF_OPTS += \
	-DLLVM_ENABLE_MODULES=OFF \
	-DLLVM_ENABLE_MODULE_DEBUGGING=OFF
LLVM_CONF_OPTS += \
	-DLLVM_ENABLE_MODULES=OFF \
	-DLLVM_ENABLE_MODULE_DEBUGGING=OFF

# Don't change the standard library to libc++.
HOST_LLVM_CONF_OPTS += -DLLVM_ENABLE_LIBCXX=OFF
LLVM_CONF_OPTS += -DLLVM_ENABLE_LIBCXX=OFF

# Don't use lld as a linker.
HOST_LLVM_CONF_OPTS += -DLLVM_ENABLE_LLD=OFF
LLVM_CONF_OPTS += -DLLVM_ENABLE_LLD=OFF

# Generate code for the target. LLVM selects a target by looking at the
# toolchain tuple
HOST_LLVM_CONF_OPTS += -DLLVM_DEFAULT_TARGET_TRIPLE=$(GNU_TARGET_NAME)
LLVM_CONF_OPTS += -DLLVM_DEFAULT_TARGET_TRIPLE=$(GNU_TARGET_NAME)

# LLVM_HOST_TRIPLE has a misleading name, it is in fact the triple of the
# system where llvm is going to run on. We need to specify triple for native
# code generation on the target.
# This solves "No available targets are compatible for this triple" with llvmpipe
LLVM_CONF_OPTS += -DLLVM_HOST_TRIPLE=$(GNU_TARGET_NAME)

# Building the Go and OCaml bindings is yet unsupported.
HOST_LLVM_CONF_OPTS += \
	-DLLVM_ENABLE_BINDINGS=OFF

# Builds a release host tablegen that gets used during the LLVM build.
HOST_LLVM_CONF_OPTS += -DLLVM_OPTIMIZED_TABLEGEN=ON

# Keep llvm utility binaries for the host. llvm-tblgen is built anyway as
# CMakeLists.txt has add_subdirectory(utils/TableGen) unconditionally.
HOST_LLVM_CONF_OPTS += \
	-DLLVM_BUILD_UTILS=ON \
	-DLLVM_INCLUDE_UTILS=ON \
	-DLLVM_INSTALL_UTILS=ON
LLVM_CONF_OPTS += \
	-DLLVM_BUILD_UTILS=OFF \
	-DLLVM_INCLUDE_UTILS=OFF \
	-DLLVM_INSTALL_UTILS=OFF

HOST_LLVM_CONF_OPTS += \
	-DLLVM_INCLUDE_TOOLS=ON \
	-DLLVM_BUILD_TOOLS=ON

# We need to activate LLVM_INCLUDE_TOOLS, otherwise it does not generate
# libLLVM.so
LLVM_CONF_OPTS += \
	-DLLVM_INCLUDE_TOOLS=ON

ifeq ($(BR2_PACKAGE_LLVM_RTTI),y)
HOST_LLVM_CONF_OPTS += -DLLVM_ENABLE_RTTI=ON
LLVM_CONF_OPTS += -DLLVM_ENABLE_RTTI=ON
else
HOST_LLVM_CONF_OPTS += -DLLVM_ENABLE_RTTI=OFF
LLVM_CONF_OPTS += -DLLVM_ENABLE_RTTI=OFF
endif

HOST_LLVM_CONF_OPTS += -DLLVM_ENABLE_DUMP=OFF
ifeq ($(BR2_PACKAGE_LLVM_DUMP),y)
LLVM_CONF_OPTS += -DLLVM_ENABLE_DUMP=ON
else
LLVM_CONF_OPTS += -DLLVM_ENABLE_DUMP=OFF
endif

# Compiler-rt not in the source tree.
# llvm runtime libraries are not in the source tree.
# Polly is not in the source tree.
HOST_LLVM_CONF_OPTS += \
	-DLLVM_BUILD_EXTERNAL_COMPILER_RT=OFF \
	-DLLVM_BUILD_RUNTIME=OFF \
	-DLLVM_INCLUDE_RUNTIMES=OFF
LLVM_CONF_OPTS += \
	-DLLVM_BUILD_EXTERNAL_COMPILER_RT=OFF \
	-DLLVM_BUILD_RUNTIME=OFF \
	-DLLVM_INCLUDE_RUNTIMES=OFF

HOST_LLVM_CONF_OPTS += \
	-DLLVM_ENABLE_WARNINGS=ON \
	-DLLVM_ENABLE_PEDANTIC=ON \
	-DLLVM_ENABLE_WERROR=OFF
LLVM_CONF_OPTS += \
	-DLLVM_ENABLE_WARNINGS=ON \
	-DLLVM_ENABLE_PEDANTIC=ON \
	-DLLVM_ENABLE_WERROR=OFF

HOST_LLVM_CONF_OPTS += \
	-DLLVM_BUILD_EXAMPLES=OFF \
	-DLLVM_BUILD_DOCS=OFF \
	-DLLVM_BUILD_TESTS=OFF \
	-DLLVM_ENABLE_DOXYGEN=OFF \
	-DLLVM_ENABLE_OCAMLDOC=OFF \
	-DLLVM_ENABLE_SPHINX=OFF \
	-DLLVM_INCLUDE_EXAMPLES=OFF \
	-DLLVM_INCLUDE_DOCS=OFF \
	-DLLVM_INCLUDE_GO_TESTS=OFF \
	-DLLVM_INCLUDE_TESTS=OFF \
	-DLLVM_INCLUDE_BENCHMARKS=OFF
LLVM_CONF_OPTS += \
	-DLLVM_BUILD_EXAMPLES=OFF \
	-DLLVM_BUILD_DOCS=OFF \
	-DLLVM_BUILD_TESTS=OFF \
	-DLLVM_ENABLE_DOXYGEN=OFF \
	-DLLVM_ENABLE_OCAMLDOC=OFF \
	-DLLVM_ENABLE_SPHINX=OFF \
	-DLLVM_INCLUDE_EXAMPLES=OFF \
	-DLLVM_INCLUDE_DOCS=OFF \
	-DLLVM_INCLUDE_GO_TESTS=OFF \
	-DLLVM_INCLUDE_TESTS=OFF \
	-DLLVM_INCLUDE_BENCHMARKS=OFF

# Copy llvm-config (host variant) to STAGING_DIR
# llvm-config (host variant) returns include and lib directories
# for the host if it's installed in host/bin:
# output/host/bin/llvm-config --includedir
# output/host/include
# When installed in STAGING_DIR, llvm-config returns include and lib
# directories from STAGING_DIR.
# output/staging/usr/bin/llvm-config --includedir
# output/staging/usr/include
define LLVM_COPY_LLVM_CONFIG_TO_STAGING_DIR
	$(INSTALL) -D -m 0755 $(HOST_DIR)/bin/llvm-config \
		$(STAGING_DIR)/usr/bin/llvm-config
endef
HOST_LLVM_POST_INSTALL_HOOKS = LLVM_COPY_LLVM_CONFIG_TO_STAGING_DIR

# The llvm-symbolizer binary is used by the Compiler-RT Fuzzer
# and AddressSanitizer tools on the target for stack traces.
# If we set -DLLVM_BUILD_TOOLS=ON this will also install the llvm-config
# target binary to STAGING_DIR, which means we can no longer run it.
# Therefore, overwrite it again with the host llvm-config.
ifeq ($(BR2_PACKAGE_COMPILER_RT),y)
LLVM_CONF_OPTS += \
	-DLLVM_BUILD_TOOLS=ON
LLVM_POST_INSTALL_STAGING_HOOKS = LLVM_COPY_LLVM_CONFIG_TO_STAGING_DIR
else
LLVM_CONF_OPTS += \
	-DLLVM_BUILD_TOOLS=OFF
endif

# By default llvm-tblgen is built and installed on the target but it is
# not necessary. Also erase LLVMHello.so from /usr/lib
define LLVM_DELETE_LLVM_TBLGEN_TARGET
	rm -f $(TARGET_DIR)/usr/bin/llvm-tblgen $(TARGET_DIR)/usr/lib/LLVMHello.so
endef
LLVM_POST_INSTALL_TARGET_HOOKS = LLVM_DELETE_LLVM_TBLGEN_TARGET

$(eval $(cmake-package))
$(eval $(host-cmake-package))

else


# Two bundles, two package variants:
#
#   host-llvm : reglinux-llvm-host-<ver>-<cpu>.tar.xz   -> HOST_DIR
#   llvm      : reglinux-llvm-target-<ver>-<cpu>.tar.xz -> STAGING_DIR + TARGET_DIR
#
# Each bundle carries llvm, clang and libclc together, so their byte-identical
# CPU ladders are gone - clang.mk and libclc.mk have no download of their own
# and just depend on the right variant.
#
# The split matters because the prebuilt branch used to define ONLY the target
# package, whose EXTRACT_CMDS unpacked host/ into HOST_DIR. Anything that merely
# wanted the cross-compiler - host-mesa3d, host-spirv-llvm-translator, the
# bindgen users - therefore had to depend on `llvm`, and that dragged its
# install-target along: ~40 MB of libLLVM.so into the rootfs of boards that
# never link it (kconfig has BR2_PACKAGE_LLVM=n there, but a make-level
# dependency builds the package anyway).
LLVM_SITE = https://github.com/REG-Linux/REG-llvm-binaries/releases/download/llvm-$(LLVM_VERSION)
LLVM_SOURCE = reglinux-llvm-target-$(LLVM_VERSION)-$(REGLINUX_LLVM_CPU).tar.xz
LLVM_DEPENDENCIES = host-llvm

# Set explicitly: pkg-generic.mk only inherits _SITE/_SOURCE into the host
# namespace when they are undefined there (ifndef $(2)_SOURCE), so naming them
# here is what keeps the two variants on different tarballs.
HOST_LLVM_SITE = $(LLVM_SITE)
HOST_LLVM_SOURCE = reglinux-llvm-host-$(LLVM_VERSION)-$(REGLINUX_LLVM_CPU).tar.xz
HOST_LLVM_DEPENDENCIES = host-python3

# The prebuilt path must still populate STAGING_DIR: cross-compiled packages
# (rpcs3, spirv-llvm-translator) look up LLVM via its cmake config there.
LLVM_INSTALL_STAGING = YES



define DISABLE_LLVM_PATCHES_IF_NOT_BUILD_FROM_SOURCE
	$(foreach dir,$(call pkg-patches-dirs,$(PKG)),\
		mkdir -p $(dir)/tmp_disabled_patches ; mv -v $(dir)/*.patch $(dir)/tmp_disabled_patches/ ; \
	)
endef

define ENABLE_LLVM_PATCHES_IF_NOT_BUILD_FROM_SOURCE
	$(foreach dir,$(call pkg-patches-dirs,$(PKG)),\
		mv -v $(dir)/tmp_disabled_patches/* $(dir)/ ; rmdir $(dir)/tmp_disabled_patches ; \
	)
endef

LLVM_PRE_PATCH_HOOKS += DISABLE_LLVM_PATCHES_IF_NOT_BUILD_FROM_SOURCE
LLVM_POST_PATCH_HOOKS += ENABLE_LLVM_PATCHES_IF_NOT_BUILD_FROM_SOURCE
HOST_LLVM_PRE_PATCH_HOOKS += DISABLE_LLVM_PATCHES_IF_NOT_BUILD_FROM_SOURCE
HOST_LLVM_POST_PATCH_HOOKS += ENABLE_LLVM_PATCHES_IF_NOT_BUILD_FROM_SOURCE

# Both variants patch the SAME shared directories (package/llvm-project/llvm/ and board/patches/llvm/),
# outside the per-package dirs, so under PARALLEL_BUILD=y their PRE hooks
# race: whichever patches first moves the *.patch files aside and the
# other's mv dies with "cannot stat ... No such file or directory",
# failing .stamp_patched. Guarding the mv would only hide it - the first
# package's POST hook would then restore the patches while the second is
# still patching, and a source patch would land on a prebuilt tarball.
# Order the two patch steps instead; buildroot turns this into an
# order-only dependency on host-llvm-patch (pkg-generic.mk), so each
# move-aside/restore pair runs to completion before the next begins.
LLVM_PATCH_DEPENDENCIES = host-llvm

# The prebuilt tarball is per-CPU, so it cannot have a hash entry. Tell
# buildroot's check-hash to skip it by name (support/download/check-hash matches
# the basename against BR_NO_CHECK_HASH_FOR) instead of moving the .hash file
# aside around the download. The old PRE/POST_DOWNLOAD rename hooks were not
# failure-safe: a download error - a 404 for an unpublished asset, say - aborts
# between the two, leaving the .hash renamed to .hash.bak and the next build
# unable to find it.
BR_NO_CHECK_HASH_FOR += $(LLVM_SOURCE) $(HOST_LLVM_SOURCE)

# Both variants leave $(@D) empty and untar straight where the files belong -
# unpacking a ~600 MB bundle into the build directory only to copy it across
# would cost that much disk for nothing.
define HOST_LLVM_EXTRACT_CMDS
endef

define HOST_LLVM_INSTALL_CMDS
	tar -C $(HOST_DIR)/../ -xf $(HOST_LLVM_DL_DIR)/$(HOST_LLVM_SOURCE) host
endef

# The bundle's host binaries and libraries carry RUNPATHs from the board that
# harvested them, so point them at their own lib dir. Only needed on this path -
# a from-source host-llvm is built with -DCMAKE_INSTALL_RPATH=$(HOST_DIR)/lib
# already. This lived on host-spirv-llvm-translator until 2026-08-27, where it
# silently added all 81 patched binaries to *that* package's file list and hence
# to its prebuilt bundle.
#
# The list used to be a hand-written glob of $(HOST_DIR)/bin - llvm-*, *ll*,
# opt, bugpoint and eight more. It did cover all 69 host/bin files that
# check-host-rpath flags, but it reached only host/bin, and libLLVM.so.22.1 and
# its siblings need the same treatment: DT_RUNPATH does not carry over from the
# executable to a library's own NEEDED entries, so it is libLLVM's own RUNPATH
# that decides whether it finds libzstd.so.1. Deriving the list from the bundle
# picks those up, needs no maintenance across LLVM bumps, and cannot stray onto
# a file some dependency rsynced in.
HOST_LLVM_DEPENDENCIES += host-patchelf
define HOST_LLVM_FIX_RPATH
	$(call REGLINUX_PREBUILT_HOST_FIX_RPATH,\
		$(HOST_LLVM_DL_DIR)/$(HOST_LLVM_SOURCE),$(HOST_DIR))
endef
HOST_LLVM_POST_INSTALL_HOOKS += HOST_LLVM_FIX_RPATH

define LLVM_EXTRACT_CMDS
endef

define LLVM_INSTALL_STAGING_CMDS
	# only target/usr (cmake config, headers, libs) goes to staging; the rest
	# of target/ is rootfs skeleton and must not leak there - a var/run symlink
	# in staging breaks the per-package rsync.
	mkdir -p $(STAGING_DIR)
	tar -C $(STAGING_DIR) --strip-components=1 -xf $(LLVM_DL_DIR)/$(LLVM_SOURCE) target/usr
endef

define LLVM_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)
	tar -C $(TARGET_DIR)/../ -xf $(LLVM_DL_DIR)/$(LLVM_SOURCE) target
endef

# The target bundle carries clang's and libclc's payload too, but the hooks that
# prune them hang off packages that may not be enabled (sm8250 has
# BR2_PACKAGE_CLANG=n), so prune here where it always runs. The clang list is
# inlined because CLANG_FILES_TO_REMOVE only exists in clang.mk's source branch -
# referencing it here would expand to a bare `rm -rf`. Keep in step with
# clang.mk's CLANG_FILES_TO_REMOVE.
define LLVM_PRUNE_BUNDLED_TARGET_FILES
	rm -rf $(TARGET_DIR)/usr/bin/clang* \
		$(TARGET_DIR)/usr/bin/c-index-test \
		$(TARGET_DIR)/usr/bin/git-clang-format \
		$(TARGET_DIR)/usr/bin/scan-build \
		$(TARGET_DIR)/usr/bin/scan-view \
		$(TARGET_DIR)/usr/libexec/c++-analyzer \
		$(TARGET_DIR)/usr/libexec/ccc-analyzer \
		$(TARGET_DIR)/usr/share/clang \
		$(TARGET_DIR)/usr/share/opt-viewer \
		$(TARGET_DIR)/usr/share/scan-build \
		$(TARGET_DIR)/usr/share/scan-view \
		$(TARGET_DIR)/usr/share/man/man1/scan-build.1 \
		$(TARGET_DIR)/usr/lib/clang
endef
LLVM_POST_INSTALL_TARGET_HOOKS += LLVM_PRUNE_BUNDLED_TARGET_FILES

# The device bitcode libraries, on the other hand, are only unwanted on ARM -
# there libclc is configured with LIBCLC_TARGETS_TO_BUILD="" and all the board
# needs is the OpenCL C headers. On x86_64 the amdgcn/r600/nvptx sets are real
# content that rusticl uses, so this must carry libclc.mk's own guard rather
# than deleting unconditionally.
ifeq ($(BR2_arm)$(BR2_aarch64),y)
define LLVM_PRUNE_BUNDLED_CLC_TARGETS
	rm -rf $(TARGET_DIR)/usr/share/clc/*amdgcn* \
		$(TARGET_DIR)/usr/share/clc/*r600* \
		$(TARGET_DIR)/usr/share/clc/*nvptx* \
		$(TARGET_DIR)/usr/share/clc/*clspv*
endef
LLVM_POST_INSTALL_TARGET_HOOKS += LLVM_PRUNE_BUNDLED_CLC_TARGETS
endif

$(eval $(generic-package))
$(eval $(host-generic-package))
endif
