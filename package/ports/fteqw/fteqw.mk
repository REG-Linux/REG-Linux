################################################################################
#
# fteqw
#
################################################################################

# Version: latest commit on master as of 2026-07 (no tagged releases)
FTEQW_VERSION = f937b9d88f71fc4429db5fe56c6a98d922711b2e
FTEQW_SITE = $(call github,fte-team,fteqw,$(FTEQW_VERSION))
FTEQW_LICENSE = GPL-2.0
FTEQW_LICENSE_FILES = LICENSE

# host-zip: menusys/csaddon (see FTE_TOOL_QCC comment below) are ALL-built
# unconditionally and their CMake post-build step shells out to `zip` to
# package menusys.pk3/csaddon.pk3, regardless of any FTE_PLUG_* toggle --
# unlike the six plugins below, they can't just be turned off, so `zip`
# has to actually be available in the build environment.
FTEQW_DEPENDENCIES = sdl3 zlib libpng jpeg libogg libvorbis host-zip

# Needed for 003-gles-fallback-when-no-desktop-opengl.patch's CMake-time
# FIND_PATH(GLES2_INCLUDE_DIR GLES2/gl2.h) probe: under
# BR2_PER_PACKAGE_DIRECTORIES, this package's build only sees headers
# from packages it depends on -- GLES2/gl2.h is never visible here
# otherwise, even on boards where some other package (mesa3d,
# img-gpu-powervr, ...) already provides it system-wide. `libgles` is
# Buildroot's virtual dependency name for "whichever concrete package
# provides GLES2 on this board" (same mesa3d/img-mesa3d/libglvnd
# split every board already has); every board in this tree currently
# selects BR2_PACKAGE_HAS_LIBGLES, so this is safe everywhere, not just
# on GLES-only targets -- on boards with real desktop GL too (x86_64),
# CMake's FIND_PACKAGE(OpenGL) still wins first and this dependency
# just goes unused.
FTEQW_DEPENDENCIES += libgles

# vulkan-headers: CMakeLists.txt already has its own independent Vulkan
# probe (FIND_PATH(VULKAN_INCLUDE_DIR vulkan/vulkan.h) -> VKQUAKE, see
# around line 257 -- untouched by 003-gles-fallback-when-no-desktop-
# opengl.patch), but it was never wired up as a real build dependency,
# so vulkan/vulkan.h was never visible in this package's own
# per-package sandbox on any board and VKQUAKE never actually compiled
# in anywhere. Gate on the same BR2_PACKAGE_REGLINUX_VULKAN flag every
# other Vulkan-capable package in this tree uses (flycast, xemu, ...) --
# only pulled in on boards that actually enabled Vulkan support.
ifeq ($(BR2_PACKAGE_REGLINUX_VULKAN),y)
FTEQW_DEPENDENCIES += vulkan-headers
endif

# Out-of-tree build: the upstream CMakeLists.txt is at the repo root, not
# under engine/, and drops the "fteqw" binary straight into the build dir
# (no install-time subdirectory) since it's a single top-level
# ADD_EXECUTABLE(fteqw ...).
FTEQW_SUPPORTS_IN_SOURCE_BUILD = NO

# Use SDL3 for windowing/GL-or-GLES-or-Vulkan context creation and
# input/audio -- this is the only client backend that doesn't rely on the
# upstream CMakeLists' host-only wildcard checks for EGL/Wayland headers
# (see engine/gl/gl_videgl.c, unused entirely in the SDL3 path: SDL3 itself
# picks GL vs GLES vs Vulkan for whatever it was built with).
FTEQW_CONF_OPTS += -DFTE_DEP_SDL3=ON

# Trim dev tools and plugins we have no use for on a target device: keep
# just the merged client+server "fteqw" binary this package installs.
#
# FTE_TOOL_QCC must stay ON even though we don't ship fteqcc itself: the
# "menusys" and "csaddon" CMake targets (ALL-built by default -- they
# produce menusys.pk3/csaddon.pk3, part of the engine's normal shipped
# content, not optional extras) invoke the freshly built fteqcc as a
# host-side QuakeC compiler during the build. Disabling it breaks the
# main build ("No rule to make target 'fteqcc', needed by 'menusys'").
FTEQW_CONF_OPTS += -DFTE_ENGINE=ON
FTEQW_CONF_OPTS += -DFTE_ENGINE_SERVER_ONLY=OFF
FTEQW_CONF_OPTS += -DFTE_ENGINE_CLIENT_ONLY=OFF
FTEQW_CONF_OPTS += -DFTE_TOOL_QCCGUI=OFF
FTEQW_CONF_OPTS += -DFTE_TOOL_IQM=OFF
FTEQW_CONF_OPTS += -DFTE_TOOL_IMAGE=OFF
FTEQW_CONF_OPTS += -DFTE_TOOL_QTV=OFF
FTEQW_CONF_OPTS += -DFTE_TOOL_MASTER=OFF
FTEQW_CONF_OPTS += -DFTE_TOOL_HTTPSV=OFF
FTEQW_CONF_OPTS += -DFTE_TOOL_QCVM=OFF
# Quake3/CoD/physics plugins are unrelated to the Quake1/Hexen2 use case
# this package is wired up for -- ioquake3 already covers Quake 3.
FTEQW_CONF_OPTS += -DFTE_PLUG_QUAKE3=OFF
FTEQW_CONF_OPTS += -DFTE_PLUG_COD=OFF
FTEQW_CONF_OPTS += -DFTE_PLUG_BULLET=OFF
FTEQW_CONF_OPTS += -DFTE_PLUG_ODE=OFF
FTEQW_CONF_OPTS += -DFTE_DEP_DRACO=OFF
# Same reasoning -- QI (online mod installer), IRC/XMPP chat, HL2 format
# support, and the competitive QuakeWorld HUD are all unrelated too. (Now
# that host-zip is a dependency anyway for menusys/csaddon, above, these
# would actually build fine -- still don't want them in scope though.)
FTEQW_CONF_OPTS += -DFTE_PLUG_QI=OFF
FTEQW_CONF_OPTS += -DFTE_PLUG_EZHUD=OFF
FTEQW_CONF_OPTS += -DFTE_PLUG_IRC=OFF
FTEQW_CONF_OPTS += -DFTE_PLUG_HL2=OFF
FTEQW_CONF_OPTS += -DFTE_PLUG_MODELS=OFF
FTEQW_CONF_OPTS += -DFTE_PLUG_XMPP=OFF
# No networked/TLS/dbus features needed for local single-player use.
FTEQW_CONF_OPTS += -DFTE_DEP_GNUTLS=OFF
FTEQW_CONF_OPTS += -DFTE_DEP_DBUS=OFF

# Unlike ioquake3/yquake2, the binary itself is a normal system binary,
# not datainit'd: it carries no per-game or per-mod code (mission packs
# and mods are plain QuakeC bytecode the engine interprets at runtime via
# -basedir/-game, not a compiled game.so per mod), so it doesn't need to
# live alongside -- or wait on -- the user's ROM data to be functional.
# regmsgd's /usr/bin capability scan can see it directly, no symlink
# needed.
define FTEQW_INSTALL_TARGET_CMDS
	$(INSTALL) -D -m 0755 $(FTEQW_BUILDDIR)/fteqw $(TARGET_DIR)/usr/bin/fteqw
endef

# What DOES need datainit is the ROM folder skeleton: empty roms/quake and
# roms/hexen2 dirs so first-boot populate (S12populateshare) creates
# /userdata/roms/quake and /userdata/roms/hexen2 for the user to drop
# their own id1/hipnotic/rogue or data1/portals .pak data into.
#
# roms/quake/qw: fs.c's "-quake" gamemode entry already searches "qw"
# as an alternate to "id1" under the same basedir
# ({"id1","qw","*fte"}), so QuakeWorld data just needs to land here --
# no separate system/basedir required.
define FTEQW_INSTALL_ROMS_SKELETON
	mkdir -p $(TARGET_DIR)/usr/share/reglinux/datainit/roms/quake/qw
	mkdir -p $(TARGET_DIR)/usr/share/reglinux/datainit/roms/hexen2
endef
FTEQW_POST_INSTALL_TARGET_HOOKS += FTEQW_INSTALL_ROMS_SKELETON

# host-fteqw: the menusys/csaddon CMake targets invoke a bare "fteqcc"
# (not $<TARGET_FILE:fteqcc>) expecting to find it on PATH -- but the
# fteqcc built by the *target* build is cross-compiled for the device
# arch and can't run on the x86_64 build host at all ("fteqcc: not
# found", since it isn't installed anywhere PATH looks, and wouldn't be
# runnable there even if it were). Build a separate, host-native fteqcc
# (same source, only FTE_TOOL_QCC enabled) and depend on it so Buildroot
# stages it into this package's own per-package host/bin -- which is
# already on PATH for every package build -- before the target build
# runs, exactly the way host-cmake/host-pkgconf become available.
FTEQW_DEPENDENCIES += host-fteqw

$(eval $(cmake-package))

HOST_FTEQW_DEPENDENCIES = host-zlib host-zip
HOST_FTEQW_SUPPORTS_IN_SOURCE_BUILD = NO

HOST_FTEQW_CONF_OPTS += -DFTE_ENGINE=OFF
HOST_FTEQW_CONF_OPTS += -DFTE_ENGINE_SERVER_ONLY=OFF
HOST_FTEQW_CONF_OPTS += -DFTE_ENGINE_CLIENT_ONLY=OFF
HOST_FTEQW_CONF_OPTS += -DFTE_TOOL_QCC=ON
HOST_FTEQW_CONF_OPTS += -DFTE_TOOL_QCCGUI=OFF
HOST_FTEQW_CONF_OPTS += -DFTE_TOOL_IQM=OFF
HOST_FTEQW_CONF_OPTS += -DFTE_TOOL_IMAGE=OFF
HOST_FTEQW_CONF_OPTS += -DFTE_TOOL_QTV=OFF
HOST_FTEQW_CONF_OPTS += -DFTE_TOOL_MASTER=OFF
HOST_FTEQW_CONF_OPTS += -DFTE_TOOL_HTTPSV=OFF
HOST_FTEQW_CONF_OPTS += -DFTE_TOOL_QCVM=OFF
HOST_FTEQW_CONF_OPTS += -DFTE_PLUG_QUAKE3=OFF
HOST_FTEQW_CONF_OPTS += -DFTE_PLUG_COD=OFF
HOST_FTEQW_CONF_OPTS += -DFTE_PLUG_BULLET=OFF
HOST_FTEQW_CONF_OPTS += -DFTE_PLUG_ODE=OFF
HOST_FTEQW_CONF_OPTS += -DFTE_PLUG_QI=OFF
HOST_FTEQW_CONF_OPTS += -DFTE_PLUG_EZHUD=OFF
HOST_FTEQW_CONF_OPTS += -DFTE_PLUG_IRC=OFF
HOST_FTEQW_CONF_OPTS += -DFTE_PLUG_HL2=OFF
HOST_FTEQW_CONF_OPTS += -DFTE_PLUG_MODELS=OFF
HOST_FTEQW_CONF_OPTS += -DFTE_PLUG_XMPP=OFF
HOST_FTEQW_CONF_OPTS += -DFTE_DEP_DRACO=OFF
HOST_FTEQW_CONF_OPTS += -DFTE_DEP_GNUTLS=OFF
HOST_FTEQW_CONF_OPTS += -DFTE_DEP_DBUS=OFF
HOST_FTEQW_CONF_OPTS += -DFTE_DEP_SDL3=OFF

define HOST_FTEQW_INSTALL_CMDS
	$(INSTALL) -D -m 0755 $(HOST_FTEQW_BUILDDIR)/fteqcc $(HOST_DIR)/bin/fteqcc
endef

$(eval $(host-cmake-package))
