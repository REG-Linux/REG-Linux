################################################################################
#
# libclc
#
################################################################################
# REG remove 0001-support-out-of-tree-build.patch
LIBCLC_VERSION = $(LLVM_PROJECT_VERSION)

ifeq ($(BR2_PACKAGE_LLVM_BUILD_FROM_SOURCE),y)

LIBCLC_SITE = $(LLVM_PROJECT_SITE)
# reglinux - one shared llvm-project monolith, see llvm-project.mk
LIBCLC_SOURCE = $(LLVM_PROJECT_SOURCE)
LIBCLC_DL_SUBDIR = llvm-project
LIBCLC_SUBDIR = libclc
LIBCLC_LICENSE = Apache-2.0 with exceptions or MIT
LIBCLC_LICENSE_FILES = LICENSE.TXT
LIBCLC_SUPPORTS_IN_SOURCE_BUILD = NO
HOST_LIBCLC_SUPPORTS_IN_SOURCE_BUILD = NO

# REG - host-libclc was needed here for the prepare_builtins tool, which libclc
# dropped in LLVM 22 (with it went patch-to-fix-prepare_builtins-not-found, whose
# hunk no longer has a target). Kept as a dependency because host-mesa3d wants
# host-libclc anyway and the ordering is free.
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

$(eval $(cmake-package))
$(eval $(host-cmake-package))

else

# The prebuilt is two bundles owned by llvm.mk:
#   reglinux-llvm-host-<ver>-<cpu>.tar.xz   -> HOST_DIR    (host-llvm)
#   reglinux-llvm-target-<ver>-<cpu>.tar.xz -> TARGET_DIR  (llvm)
# Both carry libclc alongside llvm, so there is nothing to fetch or install
# here - each variant just depends on the matching llvm variant, which is what
# lets a consumer ask for host tools without dragging the rootfs payload along.
#
# _SOURCE is set to the empty string rather than left unset: buildroot's
# `$(2)_SOURCE ?=` default would otherwise invent <pkg>-<version>.tar.gz, and an
# explicitly-empty value still counts as defined, so download and extract both
# become no-ops.
LIBCLC_SOURCE =
LIBCLC_DEPENDENCIES = llvm
HOST_LIBCLC_SOURCE =
HOST_LIBCLC_DEPENDENCIES = host-llvm

$(eval $(generic-package))
$(eval $(host-generic-package))
endif
