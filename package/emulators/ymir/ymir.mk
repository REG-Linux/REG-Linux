################################################################################
#
# Ymir
#
################################################################################
# Release on Sep 10, 2025
YMIR_VERSION = v0.1.8
YMIR_SITE = https://github.com/StrikerX3/Ymir
YMIR_SITE_METHOD=git
YMIR_GIT_SUBMODULES=YES
YMIR_LICENSE = GPLv3
YMIR_DEPENDENCIES = wayland wayland-protocols libegl libxkbcommon sdl3
YMIR_DEPENDENCIES += llvm clang

YMIR_SUPPORTS_IN_SOURCE_BUILD = NO

# PCH issues with ninja
#YMIR_CMAKE_BACKEND = ninja

YMIR_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release
#YMIR_CONF_OPTS += -DCMAKE_INSTALL_PREFIX="/usr"
YMIR_CONF_OPTS += -DBUILD_SHARED_LIBS=OFF

YMIR_CONF_OPTS += -DYmir_INCLUDE_PACKAGING=OFF
YMIR_CONF_OPTS += -DYmir_DEV_BUILD=OFF
YMIR_CONF_OPTS += -DYmir_ENABLE_DEVLOG=OFF
# TODO enable IPO, clang lld/gold issue
YMIR_CONF_OPTS += -DYmir_ENABLE_IPO=OFF
YMIR_CONF_OPTS += -DYmir_EXTRA_INLINING=ON
YMIR_CONF_OPTS += -DYmir_ENABLE_TESTS=OFF
YMIR_CONF_OPTS += -DYmir_ENABLE_SANDBOX=OFF
YMIR_CONF_OPTS += -DYmir_ENABLE_YMDASM=OFF
YMIR_CONF_OPTS += -DYmir_ENABLE_IMGUI_DEMO=OFF

# Compile with clang (skip toolchain wrapper for now because or march/mcpu/mtune)
YMIR_CONF_OPTS += -DCMAKE_C_COMPILER=$(HOST_DIR)/bin/clang.br_real
YMIR_CONF_OPTS += -DCMAKE_CXX_COMPILER=$(HOST_DIR)/bin/clang++.br_real
YMIR_CONF_OPTS += -DCMAKE_EXE_LINKER_FLAGS="-lstdc++ -lm"

# Hacks
#YMIR_CONF_OPTS += -DCMAKE_AR=$(HOST_DIR)/bin/llvm-ar
#YMIR_CONF_OPTS += -DCMAKE_RANLIB=$(HOST_DIR)/bin/llvm-ranlib
#YMIR_CONF_OPTS += -DCMAKE_LINKER=$(HOST_DIR)/bin/lld
#YMIR_CONF_OPTS += -DCMAKE_EXE_LINKER=$(HOST_DIR)/bin/llvm-link
#YMIR_CONF_OPTS += -DCMAKE_C_COMPILER_WORKS=TRUE
#YMIR_CONF_OPTS += -DCMAKE_TRY_COMPILE_TARGET_TYPE=STATIC_LIBRARY
#YMIR_CONF_OPTS += -DCMAKE_EXE_LINKER_FLAGS="-fuse-ld=bfd -lstdc++"

# TODO AVX2 for x86_64_v3
ifeq ($(BR2_x86_x86_64_v3),y)
YMIR_CONF_OPTS += -DYmir_AVX2=ON
endif

define YMIR_INSTALL_BINARY
	mkdir -p $(TARGET_DIR)/usr/bin
	cp $(@D)/buildroot-build/apps/ymir-sdl3/ymir-sdl3-* $(TARGET_DIR)/usr/bin/ymir
endef

YMIR_POST_INSTALL_TARGET_HOOKS += YMIR_INSTALL_BINARY

$(eval $(cmake-package))
