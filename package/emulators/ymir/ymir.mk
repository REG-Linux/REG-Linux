################################################################################
#
# Ymir
#
################################################################################

YMIR_VERSION = v0.3.3
YMIR_SITE = https://github.com/StrikerX3/Ymir
YMIR_SITE_METHOD = git
YMIR_GIT_SUBMODULES = YES
YMIR_LICENSE = GPLv3

# Core dependencies
YMIR_DEPENDENCIES = wayland wayland-protocols libegl libxkbcommon sdl3
YMIR_DEPENDENCIES += host-clang fmt cereal cxxopts date libcurl nghttp3
YMIR_DEPENDENCIES += rtmidi semver stb tomlplusplus json-for-modern-cpp
YMIR_DEPENDENCIES += minizip-zlib zstd
# host-lld: Ymir_ENABLE_IPO below (CMakeLists.txt's own set_property(...
# INTERPROCEDURAL_OPTIMIZATION TRUE), plus -fuse-ld=lld already forced in
# YMIR_CONF_OPTS) needs an actual lld to link the resulting ThinLTO
# bitcode - host binutils ld can't read it ("file format not
# recognized"). Not implied by host-clang (HOST_CLANG_DEPENDENCIES =
# host-llvm host-libxml2, no lld). Previously only reached via this
# package's Config.in doing `select BR2_PACKAGE_HOST_LLD if BR2_x86_64 &&
# BR2_PACKAGE_LLVM_BUILD_FROM_SOURCE` - BR2_PACKAGE_LLVM_BUILD_FROM_SOURCE
# defaults n (package/system/reglinux-system/Config.in), so that select
# never fired in the normal prebuilt-LLVM-tarball configuration, and it
# never covered aarch64 either. Same underlying per-package-snapshot gap
# already fixed the same way for rpcs3/pcsx2/xenia-edge - see
# package/emulators/rpcs3/rpcs3.mk's own host-lld/host-llvm comment.
#
# host-llvm: for llvm-ar/llvm-ranlib below - ymir-core (BUILD_SHARED_LIBS
# =OFF, so a static lib) archives those same ThinLTO bitcode objects, and
# GNU ar/ranlib can only build a correct symbol index for them with the
# gold plugin, which this toolchain doesn't carry.
YMIR_DEPENDENCIES += host-lld host-llvm

YMIR_SUPPORTS_IN_SOURCE_BUILD = NO
YMIR_CMAKE_BACKEND = ninja

YMIR_CONF_OPTS = -DCMAKE_BUILD_TYPE=Release
YMIR_CONF_OPTS += -DStb_INCLUDE_DIR=$(STAGING_DIR)/usr/include/stb
YMIR_CONF_OPTS += -DBUILD_SHARED_LIBS=OFF

# Ymir build options
YMIR_CONF_OPTS += -DYmir_INCLUDE_PACKAGING=OFF
YMIR_CONF_OPTS += -DYmir_DEV_BUILD=OFF
YMIR_CONF_OPTS += -DYmir_ENABLE_DEVLOG=OFF
YMIR_CONF_OPTS += -DYmir_ENABLE_UPDATE_CHECKS=OFF
YMIR_CONF_OPTS += -DYmir_EXTRA_INLINING=ON
YMIR_CONF_OPTS += -DYmir_ENABLE_TESTS=OFF
YMIR_CONF_OPTS += -DYmir_ENABLE_SANDBOX=OFF
YMIR_CONF_OPTS += -DYmir_ENABLE_YMDASM=OFF
YMIR_CONF_OPTS += -DYmir_ENABLE_IMGUI_DEMO=OFF

# Use clang compiler (required for C++20 features and architecture optimizations)
YMIR_CONF_OPTS += -DCMAKE_C_COMPILER=$(HOST_DIR)/bin/clang.br_real
YMIR_CONF_OPTS += -DCMAKE_CXX_COMPILER=$(HOST_DIR)/bin/clang++.br_real
YMIR_CONF_OPTS += -DYmir_ENABLE_IPO=ON
YMIR_CONF_OPTS += -DCMAKE_C_FLAGS="-fuse-ld=lld"
YMIR_CONF_OPTS += -DCMAKE_CXX_FLAGS="-fuse-ld=lld"
YMIR_CONF_OPTS += -DCMAKE_EXE_LINKER_FLAGS="-fuse-ld=lld -lstdc++ -lm"
# llvm-ar/llvm-ranlib: see the host-llvm dependency comment above - GNU
# ar/ranlib can't build a correct symbol index for ymir-core's ThinLTO
# bitcode objects without the gold plugin, which this toolchain doesn't
# carry; llvm-ar/llvm-ranlib understand bitcode natively. No .br_real
# variant needed - unlike clang/clang++, these aren't compiler-driver
# wrapper scripts that inject board-specific flags, just plain binaries.
YMIR_CONF_OPTS += -DCMAKE_AR=$(HOST_DIR)/bin/llvm-ar
YMIR_CONF_OPTS += -DCMAKE_RANLIB=$(HOST_DIR)/bin/llvm-ranlib

# Enable AVX2 for x86_64_v3
ifeq ($(BR2_x86_x86_64_v3),y)
YMIR_CONF_OPTS += -DYmir_AVX2=ON
endif

define YMIR_INSTALL_TARGET_CMDS
	$(INSTALL) -D -m 0755 $(@D)/buildroot-build/apps/ymir-sdl3/ymir-sdl3-* \
		$(TARGET_DIR)/usr/bin/ymir
endef

$(eval $(cmake-package))
