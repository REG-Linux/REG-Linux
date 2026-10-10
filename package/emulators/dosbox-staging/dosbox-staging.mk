################################################################################
#
# dosbox-staging
#
################################################################################

# Release 0.83.0 on Aug 27, 2026
DOSBOX_STAGING_VERSION = v0.83.0
DOSBOX_STAGING_SITE = $(call github,dosbox-staging,dosbox-staging,$(DOSBOX_STAGING_VERSION))
DOSBOX_STAGING_DEPENDENCIES = alsa-lib asio sdl2 sdl2_net sdl2_image zlib libpng libogg libvorbis opus opusfile slirp iir speexdsp fluidsynth libmt32emu
DOSBOX_STAGING_LICENSE = GPLv2

DOSBOX_STAGING_CPPFLAGS = -DNDEBUG
DOSBOX_STAGING_CFLAGS   = -O3 -fstrict-aliasing -fno-signed-zeros -fno-trapping-math -fassociative-math -frename-registers -ffunction-sections -fdata-sections
DOSBOX_STAGING_CXXFLAGS = -O3 -fstrict-aliasing -fno-signed-zeros -fno-trapping-math -fassociative-math -frename-registers -ffunction-sections -fdata-sections

# 0.83.0 is upstream's last meson release; main is CMake-only. Build the CMake
# side already shipped here, both to follow upstream and because the meson path
# is actively harmful when cross compiling: use_zlib_ng defaults to 'native',
# and meson.build turns that into a project-wide -march=native as soon as
# cc.has_argument('-march=native') succeeds. A cross compiler accepts the flag
# but resolves "native" against the *build* host, so binaries inherit the
# builder's CPU -- x86_64_v3 built on a Zen 4 box emitted AVX-512 (vmovdqu8
# %ymm0) and died with SIGILL on Haswell. The CMake build has no -march
# handling at all. It also already carries everything the meson build needed
# patching for: bundled riffcpp is wired up (src/libs/CMakeLists.txt), the
# resource tree is globbed rather than listed by hand (so no stale 'misc'
# shader dir), DOSBOX_VERSION_SHORT is defined in dosbox_config.h.in.cmake, and
# midi_synth.cpp is in the source list.

# Keep the source tree clean: pkg-cmake defaults to an in-source build, which
# would put the binary and the copied resource tree at the top of $(@D).
DOSBOX_STAGING_SUPPORTS_IN_SOURCE_BUILD = NO

# The tree only tests preset configurations and warns (and lists every preset)
# when it does not recognise one, so claim one. USE_SYSTEM_LIBS is what both
# the debug-linux and release-linux presets set, and it is undeclared
# elsewhere: without it src/libs/decoders looks for OpusFileConfig.cmake (the
# vcpkg-exported target) instead of probing pkg-config for opusfile, and
# configure dies since Buildroot ships opusfile.pc and no CMake config.
DOSBOX_STAGING_CONF_OPTS += -DIS_PRESET_USED=ON -DUSE_SYSTEM_LIBS=ON

# GTest is not in staging, and unit tests are of no use on target.
DOSBOX_STAGING_CONF_OPTS += -DOPT_TESTS=OFF -DOPT_DOCUMENTATION=OFF

# OpenGL support (no GLES support yet). Needs patch 002 to be honoured: stock
# CMakeLists probes and links libGL unconditionally.
ifeq ($(BR2_PACKAGE_HAS_LIBGL),y)
DOSBOX_STAGING_DEPENDENCIES += libgl
DOSBOX_STAGING_CONF_OPTS += -DOPT_OPENGL=ON
else
DOSBOX_STAGING_CONF_OPTS += -DOPT_OPENGL=OFF
endif

# Roland MT-32 emulation. Unlike meson, the CMake build links fluidsynth and
# compiles src/midi/fluidsynth.cpp with no feature gate at all, so FluidSynth
# is a hard dependency here and Config.in selects it; only MT-32 stays
# switchable (again via patch 002).
DOSBOX_STAGING_CONF_OPTS += -DOPT_MT32EMU=ON

# ManyMouse wants X Input 2.0; we have no X server on target.
DOSBOX_STAGING_CONF_OPTS += -DOPT_XINPUT=OFF

# The binary alone is not a usable install: dosbox-staging aborts during
# RENDER_Init with "Fallback shader file 'interpolation/bilinear' not found
# and is mandatory" (verified on sm8250 -- every launch died before reaching
# the DOS prompt). Upstream's install puts contrib/resources under
# $(datadir)/dosbox-staging, which support.cpp's GetResourceParentPaths()
# finds via GetExecutablePath()/"../share"/dosbox-staging; this recipe
# overrides install_target_cmds and so skips that step entirely. Stage the
# tree add_copy_assets() already assembled next to the binary (~3 MB: shaders,
# FreeDOS code pages/keyboards, mapper presets, translations, auto-mounted
# drives).
define DOSBOX_STAGING_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/buildroot-build/dosbox $(TARGET_DIR)/usr/bin/dosbox-staging
	mkdir -p $(TARGET_DIR)/usr/share/dosbox-staging
	cp -a $(@D)/buildroot-build/resources/. $(TARGET_DIR)/usr/share/dosbox-staging/
endef

$(eval $(cmake-package))
