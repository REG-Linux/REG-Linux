################################################################################
#
# llvm-libunwind
#
################################################################################

LLVM_LIBUNWIND_VERSION = $(LLVM_PROJECT_VERSION)
LLVM_LIBUNWIND_SITE = $(LLVM_PROJECT_SITE)
# reglinux - one shared llvm-project monolith, see llvm-project.mk
LLVM_LIBUNWIND_SOURCE = $(LLVM_PROJECT_SOURCE)
LLVM_LIBUNWIND_DL_SUBDIR = llvm-project
LLVM_LIBUNWIND_SUBDIR = libunwind
LLVM_LIBUNWIND_LICENSE = Apache-2.0 with exceptions
LLVM_LIBUNWIND_LICENSE_FILES = LICENSE.TXT
LLVM_LIBUNWIND_SUPPORTS_IN_SOURCE_BUILD = NO

HOST_LLVM_LIBUNWIND_DEPENDENCIES = host-llvm-cmake
HOST_LLVM_LIBUNWIND_CONF_OPTS += \
	-DCMAKE_MODULE_PATH="$(HOST_DIR)/lib/cmake/llvm/Modules" \
	-DLLVM_COMMON_CMAKE_UTILS="$(HOST_DIR)/lib/cmake/llvm" \
	-DLIBUNWIND_INSTALL_HEADERS=ON

$(eval $(host-cmake-package))
