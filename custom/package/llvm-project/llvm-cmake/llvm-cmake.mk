################################################################################
#
# llvm-cmake
#
################################################################################

LLVM_CMAKE_VERSION = $(LLVM_PROJECT_VERSION)
LLVM_CMAKE_SITE = $(LLVM_PROJECT_SITE)
# reglinux - one shared llvm-project monolith, see llvm-project.mk. No _SUBDIR
# here on purpose: this package needs two directories out of the tarball, so it
# builds from the monolith root.
LLVM_CMAKE_SOURCE = $(LLVM_PROJECT_SOURCE)
LLVM_CMAKE_DL_SUBDIR = llvm-project
LLVM_CMAKE_LICENSE = Apache-2.0 with exceptions

# LLVM 19 moved shared cmake helpers (HandleFlags, HandleLitArguments,
# WarningFlags) into runtimes/; libunwind/libcxx include them via
# CMAKE_MODULE_PATH. Both directories now come out of the one monolith, so the
# separate runtimes-*.src.tar.xz EXTRA_DOWNLOADS this used to need is gone -
# which also retires the HOST_-prefix trap that made it silently not download
# (pkg-generic.mk forwards _SOURCE/_SITE/_PATCH to the host namespace, but not
# _EXTRA_DOWNLOADS).
define HOST_LLVM_CMAKE_INSTALL_CMDS
    # reglinux - fix Modules directory below...
	mkdir -p $(HOST_DIR)/lib/cmake/llvm/Modules
	cp -Rv $(@D)/cmake/Modules/* $(HOST_DIR)/lib/cmake/llvm/Modules
	cp -Rv $(@D)/runtimes/cmake/Modules/* $(HOST_DIR)/lib/cmake/llvm/Modules
endef

$(eval $(host-generic-package))
