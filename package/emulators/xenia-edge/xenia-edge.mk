################################################################################
#
# xenia-edge
#
################################################################################
# Community fork of xenia-canary. Pinned to the edge branch HEAD as of
# 2026-09-01 - not a tag, this project doesn't cut them.
XENIA_EDGE_VERSION = 7be830a2dd9c7336dedea5f134d0f79adcefb46e
XENIA_EDGE_SITE = https://github.com/has207/xenia-edge
XENIA_EDGE_SITE_METHOD = git
XENIA_EDGE_GIT_SUBMODULES = YES
XENIA_EDGE_LICENSE = BSD-3-Clause
XENIA_EDGE_LICENSE_FILE = LICENSE

# xlib_libX11 + xlib_libXext: edge vendors SDL3 (canary still uses SDL2),
# and SDL3's own CMakeLists hard-fails configure if it finds neither X11
# nor Wayland dev libs. Not a REG-Linux-side gap to route around with
# Wayland deps (tried that first for SDL3 specifically, wrong call there)
# - edge's own third_party/CMakeLists.txt forces `set(SDL_WAYLAND OFF
# CACHE INTERNAL "")` unconditionally, with the comment "SDL_VIDEO and
# SDL_X11 must stay on: system_gnulinux.cc dlopens [libX11 at runtime]".
# X11 is the only backend SDL3 will ever select here, on every board.
# Matches the baseline of package/libraries/sdl3/sdl3.mk's own X11
# dependency block; the optional extras there (Xcursor/Xtst/Xi/
# XScrnSaver) are moot since edge's third_party/CMakeLists.txt
# force-disables those specific SDL3 options too.
#
# wayland + wayland-protocols + libxkbcommon: unrelated to SDL3 above -
# these are for wxWidgets' own (also vendored) Wayland pointer-warp
# cursor feature, gated on wxUSE_WAYLAND. Without them declared here
# explicitly, wayland-scanner and the wxUSE_WAYLAND-driven pointer-warp-v1
# codegen were only ever reaching this build indirectly, riding along in
# libgtk3's own per-package snapshot (buildroot's per-package host tree
# for a package is a merged view of everything that package itself
# needed, not just its own output) - present, but never a first-class
# dependency of this package, so nothing here actually guaranteed a
# working/current copy. Declaring them directly is more robust regardless
# of whether it was the root cause of wayland-scanner's codegen silently
# producing nothing (see git history: first attempt just disabled
# wxUSE_WAYLAND outright without pinning down why).
XENIA_EDGE_DEPENDENCIES = python-toml host-clang libgtk3 sdl2 host-sdl2 xlib_libX11 xlib_libXext wayland wayland-protocols libxkbcommon
# host-lld/host-llvm: edge's own CMakeLists.txt wants -flto=thin +
# -fuse-ld=lld for Release by default (XENIA_ENABLE_LTO, see
# CMakeLists.txt around XENIA_ENABLE_LTO - it self-wires
# add_link_options(-fuse-ld=lld) and find_program()'s llvm-ar/llvm-ranlib
# into CMAKE_AR/CMAKE_RANLIB itself, FATAL_ERROR if it can't find them -
# nothing to pass on our own command line for any of this, just needs
# ld.lld/llvm-ar/llvm-ranlib to actually resolve via PATH, which is what
# these two dependencies exist for. Same gap as rpcs3/pcsx2 (see
# package/emulators/rpcs3/rpcs3.mk's own host-lld/host-llvm comment) -
# now that host-lld is wired through prebuild-llvm.sh's tarball harvest,
# dropped the --disable-lto workaround below.
XENIA_EDGE_DEPENDENCIES += host-lld host-llvm

# edge's xenia-build.py collapsed xenia-canary's separate "premake" +
# "build" steps into one "build" subcommand (it runs cmake configure itself
# unless --no_configure) - so there is no XENIA_EDGE_CONFIGURE_CMDS.
#
# CC/CXX: unlike xenia-canary (x86_64-only), this package gets built on
# aarch64 boards too (experimental a64 JIT backend). The plain
# $(HOST_DIR)/bin/clang wrapper bakes in this board's
# BR2_TARGET_OPTIMIZATION -mtune unconditionally, and on Big.LITTLE aarch64
# boards (e.g. sm8250's -mtune=cortex-a76.cortex-a55) clang rejects that
# spelling outright. The .br_real suffix calls the real clang binary
# directly, bypassing the wrapper's flag injection - same fix as
# rpcs3.mk/pcsx2.mk. x86_64's wrapper carries no such incompatible flag, so
# it stays on the plain (already-verified-working) wrapper path.
ifeq ($(BR2_aarch64),y)
XENIA_EDGE_CC = $(HOST_DIR)/bin/clang.br_real
XENIA_EDGE_CXX = $(HOST_DIR)/bin/clang++.br_real
XENIA_EDGE_SYSTEM_PROCESSOR = aarch64
else
XENIA_EDGE_CC = $(HOST_DIR)/bin/clang
XENIA_EDGE_CXX = $(HOST_DIR)/bin/clang++
XENIA_EDGE_SYSTEM_PROCESSOR = x86_64
endif

# CFLAGS/CXXFLAGS/LDFLAGS: xenia-build.py's own run_cmake_configure() never
# sets CMAKE_SYSROOT/CMAKE_FIND_ROOT_PATH (it has no concept of a buildroot
# cross toolchain file, unlike rpcs3.mk's $(eval $(cmake-package))), and
# the plain clang wrapper's own implicit --sysroot injection is exactly
# what .br_real bypasses above. Without an explicit --sysroot here,
# clang.br_real falls back to host crt paths and ld fails to find
# Scrt1.o/crti.o. CMake seeds CMAKE_<LANG>_FLAGS from these three env vars
# on a build dir's first configure (same as autotools), so this reaches
# both the compile and link lines without a CMakeLists patch. Applied on
# both arches for robustness, even though x86_64's non-.br_real wrapper
# already injects its own --sysroot.
#
# -lstdc++ -lm on LDFLAGS: this host clang/clang++ wrapper does not
# reliably auto-link libstdc++ the way a real clang++ driver would (same
# quirk rpcs3.mk/pcsx2.mk already work around via
# -DCMAKE_EXE_LINKER_FLAGS="-lm -lstdc++") - link fails deep in vendored
# third_party static libs (SPIRV-Tools, glslang, ...) with "undefined
# reference to operator new/delete", std::ostream symbols, etc. libstdc++
# is a shared lib here, so its position on the command line ahead of
# -Wl,--start-group is fine: unlike a static archive, a DSO stays
# available to resolve undefined symbols from objects that come later.
# CMAKE_FIND_ROOT_PATH: --sysroot above only steers the compiler driver
# (crt objects, -I/-L search). SDL3's CheckX11 macro uses CMake's own
# find_package(X11)/find_path/find_library, which search hardcoded host
# paths (/usr/include/X11 etc.) and ignore STAGING_DIR entirely unless
# CMAKE_FIND_ROOT_PATH is set - which xenia-build.py's
# run_cmake_configure() never does (no buildroot toolchain file involved
# here, unlike rpcs3/pcsx2's $(eval $(cmake-package))). xlib_libX11 and
# xlib_libXext land in the per-package sysroot fine, CMake just never
# looked there.
#
# SYSTEM_PROCESSOR: without CMAKE_SYSTEM_PROCESSOR set explicitly, CMake
# derives it from whatever this script itself runs on (the x86_64 build
# host), never mind what clang.br_real actually targets.
# src/xenia/base/xe_target.cc's XE_TARGET_AARCH64/XE_TARGET_X86_64
# detection reads that variable at configure time, so a wrong value
# silently selects the wrong CPU JIT backend (x64/Xbyak instead of
# a64/xbyak_aarch64 on an aarch64 board) - it configures cleanly and only
# fails much later, deep inside backend/x64, on x86 inline asm an
# aarch64-targeting clang can't compile.
#
# xenia-build.py's "build" subcommand forwards a trailing `-- <args>` to
# BOTH its cmake-configure call AND its later `cmake --build <dir>` call
# (same pass_args list, appended in two different places) - the latter
# doesn't accept -D cache-var args, so that route breaks the build step
# that otherwise already works. 002-cmake-find-root-path.patch adds these
# defines (CMAKE_FIND_ROOT_PATH* and CMAKE_SYSTEM_NAME/PROCESSOR) straight
# into run_cmake_configure()'s own arg list instead, reaching only the
# configure invocation.
#
# "./xenia-build.py slang &&": src/xenia/gpu/vulkan needs the Slang shader
# compiler at configure time (cmake/XeniaHelpers.cmake hard-errors
# "slangc not found" otherwise) and it isn't a package anywhere - upstream
# CI fetches it as its own cache/download step, `slang` is xenia-build.py's
# own subcommand for that (downloads a host-arch prebuilt slangc into
# $(@D)/.slang/<version>/, keyed on sys.platform/platform.machine() of
# whatever runs this - the x86_64 build host, same on every board, not the
# target arch). One more live network fetch mid-build, same as the
# game-patches git clone in XENIA_EDGE_POST_PROCESS below.
define XENIA_EDGE_BUILD_CMDS
	cd $(@D) && ./xenia-build.py slang
	cd $(@D) && \
	PKGCONFIG="$(HOST_DIR)/bin/pkg-config" \
	PKGCONFIG_CONFIG=$(STAGING_DIR)/usr/lib/pkgconfig \
	SYSROOT="$(STAGING_DIR)" \
	SDL2CONFIG="$(HOST_DIR)/bin/sdl2-config" \
	CC="$(XENIA_EDGE_CC)" \
	CXX="$(XENIA_EDGE_CXX)" \
	SYSTEM_PROCESSOR="$(XENIA_EDGE_SYSTEM_PROCESSOR)" \
	CFLAGS="--sysroot=$(STAGING_DIR)" \
	CXXFLAGS="--sysroot=$(STAGING_DIR)" \
	LDFLAGS="--sysroot=$(STAGING_DIR) -lstdc++ -lm" \
	PATH="$(HOST_DIR)/bin:$(PATH)" \
	$(if $(BR2_aarch64),XE_HOST_SHADER_CC="$(HOST_DIR)/usr/bin/xenia-shader-cc") \
	./xenia-build.py build --config=release
endef

define XENIA_EDGE_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/usr/bin
	$(TARGET_STRIP) $(@D)/build/bin/Linux/Release/xenia_edge
	cp $(@D)/build/bin/Linux/Release/xenia_edge $(TARGET_DIR)/usr/bin/
endef

define XENIA_EDGE_POST_PROCESS
	# get the latest patches - reusing xenia-canary's game-patches repo:
	# edge's .toml patch format is unchanged from canary and edge does not
	# maintain a separate patches project of its own.
	#
	# Non-fatal: this is optional supplementary content (per-game compat
	# .toml overrides), not core xenia_edge functionality - confirmed the
	# repo/branch itself is live (`git ls-remote
	# https://github.com/xenia-canary/game-patches.git` resolves refs/
	# heads/main fine), so a failure here at install-target time is the
	# build container's own network egress at that specific moment, not a
	# dead URL - matches other network fetches earlier in the same build
	# (xenia-build.py slang, the package's own git source clone)
	# succeeding while this raw git init/remote/pull sequence intermittently
	# doesn't. Hard-failing the whole package over a missing patches
	# directory isn't worth it; warn instead so it's visible without being
	# fatal.
	mkdir -p $(TARGET_DIR)/usr/share/xenia-edge/patches
	mkdir -p $(@D)/temp
	( cd $(@D)/temp && $(BR2_GIT) init && \
	  $(BR2_GIT) remote add origin https://github.com/xenia-canary/game-patches.git && \
	  $(BR2_GIT) config core.sparsecheckout true && \
	  echo "patches/*.toml" >> .git/info/sparse-checkout && \
	  GIT_TERMINAL_PROMPT=0 $(BR2_GIT) pull --depth=1 origin main && \
	  mv -f patches/*.toml $(TARGET_DIR)/usr/share/xenia-edge/patches \
	) || echo "WARNING: xenia-edge: could not fetch game-patches (network unavailable at install time) - shipping without them, rerun the build to retry"

	# Clean up the temporary directory
	rm -rf $(@D)/temp
endef

XENIA_EDGE_POST_INSTALL_TARGET_HOOKS = XENIA_EDGE_POST_PROCESS

# xenia-shader-cc is a build-time host tool (SPIR-V header codegen run
# *during* the build itself, see cmake/XeniaHelpers.cmake) that must run
# on the x86_64 build machine regardless of target arch. On aarch64
# boards, $(XENIA_EDGE_CC) above (clang.br_real) defaults to THIS
# board's own target triple (confirmed via --version:
# "Target: aarch64-buildroot-linux-gnu" - it's this board's per-package
# host-clang, not a native-x86_64 compiler), so it produces an ARM64 ELF
# for a tool that then fails to execute at build time ("not found" from
# /bin/sh is actually ENOENT on the missing aarch64 dynamic loader, not
# a missing file - confirmed via `file` on the built binary). Neither
# does the container have clang at all (see top-level Dockerfile:
# build-essential/gcc/g++ only, no clang package).
#
# host-xenia-edge below builds it with the container's system gcc/g++,
# in its own independent Buildroot-managed extraction/build tree (this
# package's usual $(1)_DEPENDENCIES += host-<name> idiom, matching
# package/ports/gzdoom/gzdoom.mk and package/gpu/vulkan/glslang/
# glslang.mk elsewhere in this tree) - not a same-build native pre-pass.
# Two earlier approaches shared this package's own build tree instead and
# both hit real architectural walls: (1) reusing xenia-build.py's default
# build/ dir let CMake's reconfigure inherit a stale cross --sysroot from
# CMAKE_CXX_FLAGS cache; (2) giving that pre-pass its own directory still
# routed pkg-config through Buildroot's target-pinned wrapper (no env var
# redirects it elsewhere), leaking an aarch64 GTK3 include path into the
# "native" gcc compile and pulling in ARM SVE-only glibc math headers. A
# real host-<name> package sidesteps both by construction: its own
# extraction directory can't inherit this package's cross-build cache,
# and 005-host-tools-only.patch's XE_HOST_TOOLS_ONLY keeps its configure
# from ever calling pkg-config for anything target-scoped in the first
# place (see that patch's own commit message).
ifeq ($(BR2_aarch64),y)
XENIA_EDGE_DEPENDENCIES += host-xenia-edge
endif

# host-lz4: xenia-shader-cc's link line inherits the top-level
# CMakeLists.txt's generic Linux link_libraries(stdc++fs dl lz4 m pthread
# rt) (gated on CMAKE_SYSTEM_NAME STREQUAL "Linux", not on
# XE_HOST_TOOLS_ONLY - it's a directory-scope property every target in
# the tree picks up, not something specific to GTK3/SDL3/wx). Nothing in
# this host build actually calls into lz4, but the linker still needs
# -llz4 to resolve; liblz4-dev isn't in the container's base image
# (Dockerfile only lists build-essential/gcc/g++), so pull the Buildroot
# host package.
HOST_XENIA_EDGE_DEPENDENCIES = host-ninja host-lz4

# CFLAGS/CXXFLAGS/LDFLAGS explicit-empty: host-generic-package's own
# environment isn't otherwise expected to carry board-cross flags the
# way a same-build pre-pass's inherited cache could, but absent still
# means "inherit whatever's there" and empty cannot - cheap insurance,
# not load-bearing.
#
# -DXENIA_ENABLE_LTO=OFF: defaults ON in CMakeLists.txt and
# unconditionally adds -flto=thin for Release (a ThinLTO flag clang
# understands and gcc does not - gcc would reject it outright).
#
# -DXE_HOST_TOOLS_ONLY=ON: 005-host-tools-only.patch's flag - skips
# GTK3/SDL3/wxWidgets/FFmpeg/src/xenia entirely, so this configure only
# ever needs xenia-shader-cc's actual deps (glslang, SPIRV-Tools-static/
# -opt, SPIRV-Headers), none of which touch pkg-config or STAGING_DIR.
#
# -DCMAKE_EXE_LINKER_FLAGS=-L$(HOST_DIR)/lib: the top-level CMakeLists.txt
# unconditionally adds link_libraries(stdc++fs dl lz4 m pthread rt) for
# every Linux target regardless of XE_HOST_TOOLS_ONLY (a directory-scope
# property, not gated with GTK3/SDL3/wx) - xenia-shader-cc inherits -llz4
# on its link line even though it never calls into lz4 itself. host-lz4
# (above) installs under $(HOST_DIR), which the linker doesn't search by
# default (it's not a standard system prefix) - point it there directly.
define HOST_XENIA_EDGE_BUILD_CMDS
	cd $(@D) && \
	CFLAGS= CXXFLAGS= LDFLAGS= \
	PATH="$(HOST_DIR)/bin:$(PATH)" \
	cmake -S . -B build -G "Ninja Multi-Config" \
	    -DCMAKE_C_COMPILER=gcc \
	    -DCMAKE_CXX_COMPILER=g++ \
	    -DXENIA_ENABLE_LTO=OFF \
	    -DXE_HOST_TOOLS_ONLY=ON \
	    -DCMAKE_EXE_LINKER_FLAGS="-L$(HOST_DIR)/lib"
	cd $(@D) && \
	PATH="$(HOST_DIR)/bin:$(PATH)" \
	cmake --build build --config Release --target xenia-shader-cc
endef

define HOST_XENIA_EDGE_INSTALL_CMDS
	$(INSTALL) -D -m 0755 $(@D)/build/host_tools/Release/xenia-shader-cc \
		$(HOST_DIR)/usr/bin/xenia-shader-cc
endef

# Both evals stay together at the very end, after every _DEPENDENCIES
# assignment above (including the += for host-xenia-edge) - matching
# package/ports/gzdoom/gzdoom.mk's own structure. Buildroot's per-package
# sync/dependency-graph wiring snapshots $(2)_DEPENDENCIES at
# $(eval $(generic-package)) time, so a DEPENDENCIES += appearing AFTER
# this point is silently dropped from xenia-edge's own build-order
# prerequisites (it can still show up in the per-package rsync's own
# --link-dest list, which is computed separately/later - that mismatch is
# exactly what produced "rsync: --link-dest arg does not exist:
# .../host-xenia-edge/host" the one time this eval was moved above the
# += instead of below it: Buildroot knew to copy host-xenia-edge's
# per-package dir but never actually built it first).
$(eval $(generic-package))
$(eval $(host-generic-package))
