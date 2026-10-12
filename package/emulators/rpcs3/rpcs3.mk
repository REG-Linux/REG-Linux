################################################################################
#
# rpcs3
#
################################################################################
# Version v0.0.43 - Commits on Oct 1, 2026
RPCS3_VERSION = v0.0.43
RPCS3_SITE = https://github.com/RPCS3/rpcs3.git
RPCS3_SITE_METHOD=git
RPCS3_GIT_SUBMODULES=YES
RPCS3_LICENSE = GPLv2
RPCS3_DEPENDENCIES += alsa-lib llvm ffmpeg libevdev libxml2 sdl3 zlib zstd pugixml
RPCS3_DEPENDENCIES += libglew libglu libpng libusb mesa3d ncurses openal rtmpdump
RPCS3_DEPENDENCIES += reglinux-qt6 libcurl rtmidi cubeb libdrm wayland libxkbcommon
RPCS3_DEPENDENCIES += host-clang
# host-lld: rpcs3_emu is built with CMake IPO (USE_LTO below -> clang
# -flto=thin bitcode objects) - host binutils ld can't read that at final
# link ("file format not recognized"), needs lld specifically. Explicit
# dependency, not implied by host-clang (HOST_CLANG_DEPENDENCIES =
# host-llvm host-libxml2, no lld) - see pcsx2.mk's own host-lld comment,
# same underlying per-package-snapshot gap, same fix.
#
# host-llvm: for llvm-ar/llvm-ranlib below. rpcs3_emu archives ThinLTO
# bitcode objects into a static lib - GNU ar/ranlib can only build a
# correct symbol index for those if built against the gold plugin
# (LLVMgold.so), which this toolchain doesn't carry; llvm-ar/llvm-ranlib
# understand bitcode natively. Already transitively present via
# host-clang's own HOST_CLANG_DEPENDENCIES = host-llvm ..., but declaring
# it directly here means rpcs3's own per-package snapshot doesn't depend
# on that staying true.
RPCS3_DEPENDENCIES += host-lld host-llvm

RPCS3_SUPPORTS_IN_SOURCE_BUILD = NO

RPCS3_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release
RPCS3_CONF_OPTS += -DCMAKE_INSTALL_PREFIX=/usr
RPCS3_CONF_OPTS += -DCMAKE_CROSSCOMPILING=ON
RPCS3_CONF_OPTS += -DBUILD_SHARED_LIBS=OFF
RPCS3_CONF_OPTS += -DUSE_NATIVE_INSTRUCTIONS=OFF
# USE_LTO: rpcs3's own CMakeLists.txt option (rpcs3/Emu/CMakeLists.txt),
# sets INTERPROCEDURAL_OPTIMIZATION ON for the rpcs3_emu static lib ->
# clang -flto=thin. host-lld (above) + CMAKE_LINKER/-fuse-ld=lld and
# CMAKE_AR/CMAKE_RANLIB=llvm-ar/llvm-ranlib (below, in the clang block)
# are what make this actually link: host-lld now wired through
# prebuild-llvm.sh's tarball harvest (was the original gap here), and
# llvm-ar/llvm-ranlib because GNU ar/ranlib can't build a correct symbol
# index for bitcode objects without the gold plugin, which this
# toolchain doesn't carry.
RPCS3_CONF_OPTS += -DUSE_LTO=ON
RPCS3_CONF_OPTS += -DLLVM_DIR=$(STAGING_DIR)/usr/lib/cmake/llvm/
RPCS3_CONF_OPTS += -DUSE_PRECOMPILED_HEADERS=OFF
RPCS3_CONF_OPTS += -DSTATIC_LINK_LLVM=OFF
RPCS3_CONF_OPTS += -DUSE_SYSTEM_CURL=ON
RPCS3_CONF_OPTS += -DUSE_SYSTEM_FFMPEG=ON
RPCS3_CONF_OPTS += -DUSE_SYSTEM_LIBPNG=ON
RPCS3_CONF_OPTS += -DUSE_SYSTEM_LIBUSB=ON
RPCS3_CONF_OPTS += -DUSE_SYSTEM_PUGIXML=ON
RPCS3_CONF_OPTS += -DUSE_SYSTEM_RTMIDI=ON
RPCS3_CONF_OPTS += -DUSE_SYSTEM_SDL=ON
RPCS3_CONF_OPTS += -DUSE_SYSTEM_CUBEB=ON
RPCS3_CONF_OPTS += -DUSE_SYSTEM_WOLFSSL=OFF
RPCS3_CONF_OPTS += -DUSE_SYSTEM_ZLIB=ON
RPCS3_CONF_OPTS += -DUSE_SYSTEM_ZSTD=ON
RPCS3_CONF_OPTS += -DUSE_SDL=ON
RPCS3_CONF_OPTS += -DUSE_LIBEVDEV=ON

RPCS3_CONF_ENV = LIBS="-ncurses -ltinfo"

ifeq ($(BR2_PACKAGE_REGLINUX_VULKAN),y)
	RPCS3_CONF_OPTS += -DUSE_VULKAN=ON
	RPCS3_DEPENDENCIES += vulkan-headers vulkan-loader
else
	RPCS3_CONF_OPTS += -DUSE_VULKAN=OFF
endif

ifeq ($(BR2_PACKAGE_WAYLAND),y)
	RPCS3_CONF_OPTS += -DUSE_WAYLAND=ON
else
	RPCS3_CONF_OPTS += -DUSE_WAYLAND=OFF
endif

# Use clang on x86_64 and every aarch64 target.
#
# Big.LITTLE targets (RK3588, MT8395, SM8250, QCS6490, SM6115) carry a
# board-level -mtune=cortex-a76.cortex-a55 via BR2_TARGET_OPTIMIZATION.
# $(HOST_DIR)/bin/clang is buildroot's compiled toolchain-wrapper binary,
# which bakes BR2_TARGET_OPTIMIZATION (that -mtune spelling included) into
# every invocation unconditionally -- confirmed via `clang: error:
# unsupported argument 'cortex-a76.cortex-a55' to option '-mtune='`, so no
# -DCMAKE_C_FLAGS override on the cmake command line can undo it (the
# wrapper injects the flag around whatever we pass). The .br_real suffix
# calls the real clang binary directly, bypassing the wrapper's flag
# injection entirely -- same pattern as ymir.mk. This is safe: CMake's own
# CMAKE_SYSROOT (already set in toolchainfile.cmake) supplies --sysroot to
# every compile itself, so we aren't losing the wrapper's sysroot injection,
# only the incompatible -mtune it also carried.
ifeq ($(BR2_PACKAGE_CLANG),y)
ifeq ($(BR2_x86_64)$(BR2_aarch64),y)
RPCS3_DEPENDENCIES += clang
# x86_64's wrapper doesn't carry an incompatible flag, so it stays on the
# plain (already-verified-working) wrapper path; only aarch64 needs .br_real.
ifeq ($(BR2_aarch64),y)
RPCS3_CONF_OPTS += -DCMAKE_C_COMPILER=$(HOST_DIR)/bin/clang.br_real
RPCS3_CONF_OPTS += -DCMAKE_CXX_COMPILER=$(HOST_DIR)/bin/clang++.br_real
RPCS3_CONF_OPTS += -DCMAKE_LINKER=$(HOST_DIR)/bin/lld.br_real
else
RPCS3_CONF_OPTS += -DCMAKE_C_COMPILER=$(HOST_DIR)/bin/clang
RPCS3_CONF_OPTS += -DCMAKE_CXX_COMPILER=$(HOST_DIR)/bin/clang++
RPCS3_CONF_OPTS += -DCMAKE_LINKER=$(HOST_DIR)/bin/lld
endif
RPCS3_CONF_OPTS += -DCMAKE_EXE_LINKER_FLAGS="-fuse-ld=lld -lm -lstdc++"
RPCS3_CONF_OPTS += -DCMAKE_SHARED_LINKER_FLAGS="-fuse-ld=lld"
RPCS3_CONF_OPTS += -DCMAKE_MODULE_LINKER_FLAGS="-fuse-ld=lld"
# llvm-ar/llvm-ranlib: see the USE_LTO/host-llvm comments above - GNU
# ar/ranlib can't build a correct symbol index for rpcs3_emu's ThinLTO
# bitcode objects without the gold plugin, which this toolchain doesn't
# carry; llvm-ar/llvm-ranlib understand bitcode natively. No .br_real
# variant needed - unlike clang/clang++, these aren't compiler-driver
# wrapper scripts that inject board-specific flags, just plain binaries.
RPCS3_CONF_OPTS += -DCMAKE_AR=$(HOST_DIR)/bin/llvm-ar
RPCS3_CONF_OPTS += -DCMAKE_RANLIB=$(HOST_DIR)/bin/llvm-ranlib
endif
endif

define RPCS3_BUILD_CMDS
	$(TARGET_CONFIGURE_OPTS) \
		$(MAKE) -C $(@D)/buildroot-build
endef

$(eval $(cmake-package))
