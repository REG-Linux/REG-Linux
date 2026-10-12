################################################################################
#
# libretro-jazz2-native
#
################################################################################

LIBRETRO_JAZZ2_NATIVE_VERSION = $(JAZZ2_NATIVE_VERSION)
LIBRETRO_JAZZ2_NATIVE_SITE = $(JAZZ2_NATIVE_SITE)
LIBRETRO_JAZZ2_NATIVE_LICENSE = GPL-3.0
LIBRETRO_JAZZ2_NATIVE_LICENSE_FILE = LICENSE

# openal is not optional despite this being a libretro core: NCINE_WITH_AUDIO
# ("Enable OpenAL support and thus sound") defaults ON, and retro_run() pulls
# each frame of mixed output from OpenAL Soft's loopback device to hand to the
# frontend. Without the dependency find_package(OpenAL) simply fails, the engine
# builds with no audio device, and renderSamples() returns false -- whereupon
# the core memsets the buffer and feeds the frontend silence to keep its pacing
# fed. It fails quietly: no build error, no runtime error, just no sound on any
# board or launch path (confirmed silent on cha/ALSA via both Libra and
# RetroArch, and on sm8250/PipeWire).
LIBRETRO_JAZZ2_NATIVE_DEPENDENCIES += zlib libopenmpt libcurl openal

LIBRETRO_JAZZ2_NATIVE_SUPPORTS_IN_SOURCE_BUILD = NO

LIBRETRO_JAZZ2_NATIVE_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release
LIBRETRO_JAZZ2_NATIVE_CONF_OPTS += -DBUILD_SHARED_LIBS=OFF
LIBRETRO_JAZZ2_NATIVE_CONF_OPTS += -DNCINE_LINUX_PACKAGE="jazz2"
LIBRETRO_JAZZ2_NATIVE_CONF_OPTS += -DNCINE_DOWNLOAD_DEPENDENCIES=OFF
LIBRETRO_JAZZ2_NATIVE_CONF_OPTS += -DNCINE_BUILD_LIBRETRO=ON

# Rendering backend. Upstream's default for a libretro build is the CPU
# rasterizer, presented through retro_video_refresh, which needs no GL context
# at all; "OpenGL" instead renders into the frontend's FBO via SET_HW_RENDER.
#
# Software is kept, and the core is instead restricted to GLES3 boards in
# Config.in.ports -- see the reasoning there. In short: the CPU rasterizer costs
# little to present (the RGBA->XRGB8888 swizzle in LibretroGfxDevice::update()
# auto-vectorizes to NEON, ~2% of one core at 720x405x60), and it renders at the
# same 720x405 internal resolution the standalone uses, so it is not what makes
# a slow board slow. What a slow board cannot survive is libretro's audio
# contract, which ties one frame of samples to one retro_run. Measured: 58 fps
# with clean audio on sm8250; on cha the engine manages 12-17 fps in software
# and the sound cuts continuously, on both RetroArch and Libra.
#
# Going to the GPU would move the work off the CPU and is the natural next step
# if a weaker GLES3 board turns out not to keep up: -DNCINE_PREFERRED_RHI=OpenGL,
# which needs no profile override now that the core is GLES3-only (upstream's
# hardware default is ES 3.0). 002-allow-gles2-profile.patch is what would let
# an ES 2.0 profile through instead, and records why that path could never be
# launched from external RetroArch on a GLES2 board: SET_HW_RENDER is not a
# capability query, so it only worked under Libra, which hands the core the
# frontend's existing context.
LIBRETRO_JAZZ2_NATIVE_CONF_OPTS += -DNCINE_PREFERRED_RHI=Software

# The core is useless without the engine's own asset bundle: Main.cpp's
# OverridePathsFromHost() aborts with "Cannot find \"Content\" directory in any of
# the directories provided by the frontend" when it cannot locate Content/, and
# the .so is all this package installs. These are read-only engine data
# (Animations, Metadata, Translations), hence /usr/share rather than datainit --
# the launcher points the core at them and nothing should be able to delete them.
#
# jazz2-native installs the very same tree through cmake's own install rules
# (ncine_installation.cmake: DATA_INSTALL_DESTINATION = share/jazz2/Content, from
# NCINE_LINUX_PACKAGE="jazz2"), so ship it only when that package is absent and
# the two can never write the same files.
ifneq ($(BR2_PACKAGE_JAZZ2_NATIVE),y)
define LIBRETRO_JAZZ2_NATIVE_INSTALL_CONTENT
	mkdir -p $(TARGET_DIR)/usr/share/jazz2
	cp -a $(@D)/Content $(TARGET_DIR)/usr/share/jazz2/
endef
endif

# The frontend refuses to load a core with no .info file ("missing core info
# file ..."), and the libretro-info package harvests upstream's database, which
# has no entry for this core. Ship one, with the version substituted so it
# cannot drift from the core beside it.
define LIBRETRO_JAZZ2_NATIVE_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/buildroot-build/jazz2_libretro.so \
	$(TARGET_DIR)/usr/lib/libretro/jazz2_libretro.so
	$(INSTALL) -D -m 0644 \
	    $(LIBRETRO_JAZZ2_NATIVE_PKGDIR)/jazz2_libretro.info \
	    $(TARGET_DIR)/usr/share/libretro/info/jazz2_libretro.info
	$(SED) 's|@VERSION@|$(LIBRETRO_JAZZ2_NATIVE_VERSION)|' \
	    $(TARGET_DIR)/usr/share/libretro/info/jazz2_libretro.info
	$(LIBRETRO_JAZZ2_NATIVE_INSTALL_CONTENT)
endef

$(eval $(cmake-package))
