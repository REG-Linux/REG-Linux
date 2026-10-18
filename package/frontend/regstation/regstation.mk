################################################################################
#
# REG-Station
#
################################################################################

REGSTATION_VERSION = 18aa0ba9be57891b3ed1b119d1142bd34afe9b10
# Proprietary, with open-source parts compiled in or installed with it
# (THIRD_PARTY_LICENSES). Neither the private source nor the binaries may be
# published by legal-info.
REGSTATION_LICENSE = Proprietary, MIT, BSD-2-Clause, BSD-3-Clause, Apache-2.0, OFL-1.1, Ubuntu Font Licence 1.0
REGSTATION_REDISTRIBUTE = NO
REGSTATION_DEPENDENCIES = sdl3 sdl3_mixer libyuv webp giflib
REGSTATION_DEPENDENCIES += freetype libcurl rapidjson libarchive
REGSTATION_DEPENDENCIES += lunasvg pugixml gettext host-gettext
REGSTATION_DEPENDENCIES += es-system gamecontrollerdb jpeg host-python3
REGSTATION_DEPENDENCIES += flatbuffers

ifeq ($(BR2_PACKAGE_REGSTATION_BUILD_FROM_SOURCE),y)

REGSTATION_TOKEN = $(shell cat /build/gh_token)
REGSTATION_SITE = https://$(REGSTATION_TOKEN)@github.com/REG-Linux/REG-Station
REGSTATION_SITE_METHOD = git
REGSTATION_GIT_SUBMODULES = YES

REGSTATION_SUPPORTS_IN_SOURCE_BUILD = NO
REGSTATION_LICENSE_FILES = LICENSE THIRD_PARTY_LICENSES

# No CEC input: libCEC is GPL-2.0, and CMake would link it whenever it is
# in the sysroot (every image builds it for other packages)
REGSTATION_CONF_OPTS += -DCEC=OFF

# REG investigate this, looks like an old "hack" we should remove/avoid
# Pass arch (uppercase) as compiler define
REGSTATION_CONF_OPTS += -DCMAKE_CXX_FLAGS=-D$(call UPPERCASE,$(REGLINUX_SYSTEM_ARCH))

# Always build with "batocera" special code
REGSTATION_CONF_OPTS += -DBATOCERA=ON

# Don't build tests for target
REGSTATION_CONF_OPTS += -DBUILD_TESTING=OFF

# File manager
REGSTATION_CONF_OPTS += -DENABLE_FILEMANAGER=OFF

# Force to use rs-ffmpeg LGPL
REGSTATION_CONF_OPTS += -DFFMPEG_DIR="$(STAGING_DIR)/usr/lib/rs-ffmpeg"

# Debug build settings + install in staging.
#
# RelWithDebInfo, not Debug: BR2_ENABLE_DEBUG means "build with debugging
# symbols", not "turn optimisation off" (that is BR2_ENABLE_RUNTIME_DEBUG).
# CMAKE_BUILD_TYPE=Debug made REG-Station's CMakeLists pick -O0, and an
# unoptimised frontend is not subtly slower - glm's vector/matrix operators
# stop inlining, and the gamelist spends its whole frame budget transforming
# text vertices one non-inlined call at a time (measured on the C5: a game with
# an 11k-character description ran at 12fps).
ifeq ($(BR2_ENABLE_DEBUG),y)
REGSTATION_INSTALL_STAGING = YES
REGSTATION_CONF_OPTS += -DCMAKE_BUILD_TYPE=RelWithDebInfo
endif

# GLM math configuration
REGSTATION_CONF_OPTS += -DGLM_ENABLE_CXX_20=ON
REGSTATION_CONF_OPTS += -DGLM_ENABLE_FAST_MATH=ON
# SSE2 to AVX2 for x86_64_v3
ifeq ($(BR2_x86_x86_64_v3),y)
REGSTATION_CONF_OPTS += -DGLM_ENABLE_SIMD_SSE2=ON
REGSTATION_CONF_OPTS += -DGLM_ENABLE_SIMD_SSE3=ON
REGSTATION_CONF_OPTS += -DGLM_ENABLE_SIMD_SSSE3=ON
REGSTATION_CONF_OPTS += -DGLM_ENABLE_SIMD_SSE4_1=ON
REGSTATION_CONF_OPTS += -DGLM_ENABLE_SIMD_SSE4_2=ON
REGSTATION_CONF_OPTS += -DGLM_ENABLE_SIMD_AVX=ON
REGSTATION_CONF_OPTS += -DGLM_ENABLE_SIMD_AVX2=ON
# SSE2 only for x86_64 baseline
else ifeq ($(BR2_x86_64),y)
REGSTATION_CONF_OPTS += -DGLM_ENABLE_SIMD_SSE2=ON
else ifeq ($(BR2_arm)$(BR2_aarch64),y)
# NEON for ARM/AArch64, except for rpi0/1
ifneq ($(BR2_arm1176jzf_s),y)
REGSTATION_CONF_OPTS += -DGLM_TEST_ENABLE_SIMD_NEON=ON
endif
endif

# OpenGL desktop vs GLES 2.0 renderer
ifeq ($(BR2_PACKAGE_HAS_LIBGL),y)
REGSTATION_CONF_OPTS += -DGL=ON
else ifeq ($(BR2_PACKAGE_HAS_LIBGLES),y)
REGSTATION_CONF_OPTS += -DGLES2=ON
endif

# GLES2-only GPUs: drop the SDLRenderer translation unit. Live H3 measurement
# (Mali 400 / Lima / 1080p) shows 30 -> 60 FPS on menu overlays just by routing
# through the GLES20 batched path. The auto-detect probe in REG-Station picks
# SDLRenderer wrong on these because Mesa advertises an ES3 context even when
# the HW only does ES2. Force it at build time:
#   - BR2_PACKAGE_SYSTEM_LIMA_MESA3D     => Mali 400 / 450 (sun4i, sun8i, ...)
#   - BR2_PACKAGE_SYSTEM_TARGET_BCM2835/6/7 => RPi 0 / 1 / 2 / 3 (VC4)
ifneq ($(filter y,\
        $(BR2_PACKAGE_SYSTEM_LIMA_MESA3D) \
        $(BR2_PACKAGE_SYSTEM_TARGET_BCM2835) \
        $(BR2_PACKAGE_SYSTEM_TARGET_BCM2836) \
        $(BR2_PACKAGE_SYSTEM_TARGET_BCM2837)),)
REGSTATION_CONF_OPTS += -DFORCE_GLES2_RENDERER=ON
endif

# Fatal-signal backtrace handler. A developer tool -- the addresses in its
# report only resolve against the unstripped binary in the build tree -- so it
# follows the debug build rather than shipping in release images. BR2_ENABLE_DEBUG
# is what `make <target>-build DEBUG_BUILD=y` sets (see the top-level Makefile).
ifeq ($(BR2_ENABLE_DEBUG),y)
REGSTATION_CONF_OPTS += -DENABLE_CRASH_HANDLER=ON
endif

# Text-to-speech for visually impaired people
ifeq ($(BR2_PACKAGE_ESPEAK),y)
REGSTATION_CONF_OPTS += -DENABLE_TTS=ON
REGSTATION_DEPENDENCIES += espeak
endif

# Vulkan HW rendering (optional — needs vulkan-loader).
# Gate on VULKAN_LOADER, not MESA3D_VULKAN_DRIVER, so non-Mesa Vulkan stacks
# (proprietary x86 ICDs, vendor blob ICDs) are picked up too.
ifeq ($(BR2_PACKAGE_VULKAN_LOADER),y)
REGSTATION_CONF_OPTS += -DENABLE_VULKAN=ON
REGSTATION_DEPENDENCIES += vulkan-headers vulkan-loader
else
REGSTATION_CONF_OPTS += -DENABLE_VULKAN=OFF
endif

# No Kodi
REGSTATION_CONF_OPTS += -DDISABLE_KODI=ON

# Audio (volume + device/profile) is controlled via the regmsgd IPC, so
# REG-Station no longer links libpulse/alsa-lib directly.

# Enable or disable FFMPEG depending on platform
ifeq ($(BR2_PACKAGE_RS_FFMPEG),y)
REGSTATION_CONF_OPTS += -DUSE_FFMPEG=ON
REGSTATION_DEPENDENCIES += rs-ffmpeg
else
REGSTATION_CONF_OPTS += -DUSE_FFMPEG=OFF
endif

# RetroAchievements keys
REGSTATION_CONF_OPTS += "-DCHEEVOS_DEV_LOGIN=$(shell grep -m 1 -E '^CHEEVOS_DEV_LOGIN=' $(@D)/keys.txt | cut -d = -f 2-)"

define REGSTATION_DOWNLOAD_KEYS
	# Download scrapper and retroachievements developer keys
	@wget --header="Authorization: token $(REGSTATION_TOKEN)" -O $(@D)/keys.txt "https://raw.githubusercontent.com/REG-Linux/keys/main/key.txt" || true
	# An expired/revoked gh_token leaves this file empty and the `|| true` above
	# hides it, so the build silently ships with blank scraper and
	# retroachievements dev keys -- which surfaces only as scrapers quietly not
	# working, never as an error. Warn rather than fail, so someone without
	# access to the private keys repo can still build.
	@if [ ! -s $(@D)/keys.txt ]; then \
		echo "*** WARNING: keys.txt is EMPTY -- check gh_token (expired/revoked?)."; \
		echo "***          Scraper and RetroAchievements dev keys will be blank."; \
	fi
endef

# Copy es-system translation headers into source tree so xgettext picks them up
define REGSTATION_EXTERNAL_POS
	cp $(STAGING_DIR)/usr/share/es-system/rs_external_translations.h $(@D)/src/
	cp $(STAGING_DIR)/usr/share/es-system/rs_keys_translations.h     $(@D)/src/
endef

# Resources
define REGSTATION_RESOURCES
	$(INSTALL) -m 0755 -d $(TARGET_DIR)/usr/share/regstation/resources/help
	$(INSTALL) -m 0755 -d $(TARGET_DIR)/usr/share/regstation/resources/flags
	$(INSTALL) -m 0755 -d $(TARGET_DIR)/usr/share/regstation/resources/battery
	$(INSTALL) -m 0644 -D $(@D)/resources/*.* $(TARGET_DIR)/usr/share/regstation/resources
	$(INSTALL) -m 0644 -D $(@D)/resources/help/*.* $(TARGET_DIR)/usr/share/regstation/resources/help
	$(INSTALL) -m 0644 -D $(@D)/resources/flags/*.* $(TARGET_DIR)/usr/share/regstation/resources/flags
	$(INSTALL) -m 0644 -D $(@D)/resources/battery/*.* $(TARGET_DIR)/usr/share/regstation/resources/battery

	# Licence and third-party notices; the prebuilt archive takes them from here
	$(INSTALL) -m 0644 -D $(@D)/LICENSE $(TARGET_DIR)/usr/share/regstation/LICENSE
	$(INSTALL) -m 0644 -D $(@D)/THIRD_PARTY_LICENSES $(TARGET_DIR)/usr/share/regstation/THIRD_PARTY_LICENSES
endef

### S31regstation
# default for most of architectures
REGSTATION_CMD = regstation-standalone
REGSTATION_ARGS = $${EXTRA_OPTS}
REGSTATION_POSTFIX = \&

## on Wayland sway runs ES
ifeq ($(BR2_PACKAGE_REGLINUX_SWAY),y)
REGSTATION_DEPENDENCIES += sway
REGSTATION_POST_INSTALL_TARGET_HOOKS += REGSTATION_WAYLAND_SWAY
endif

define REGSTATION_WAYLAND_SWAY
	$(INSTALL) -D -m 0755 $(REGSTATION_PKGDIR)/wayland/sway/04-sway.sh	$(TARGET_DIR)/etc/profile.d/04-sway.sh
	$(INSTALL) -D -m 0755 $(REGSTATION_PKGDIR)/wayland/sway/config		$(TARGET_DIR)/etc/sway/config
	$(INSTALL) -D -m 0755 $(REGSTATION_PKGDIR)/wayland/sway/launchconfig	$(TARGET_DIR)/etc/sway/launchconfig
	mkdir -p $(TARGET_DIR)/etc/sway/boards
	$(INSTALL) -m 0644 $(REGSTATION_PKGDIR)/wayland/sway/boards/*.conf	$(TARGET_DIR)/etc/sway/boards/
endef

## On boards where wlroots/sway misbehaves with the GPU stack (vendor
## blobs that reject the dmabuf modifiers wlroots advertises, or need a
## specific gbm-format sway has no knob for), weston runs ES instead.
## Selecting REGLINUX_WESTON without REGLINUX_SWAY routes S31regstation
## through weston-launch.
ifeq ($(BR2_PACKAGE_REGLINUX_WESTON),y)
REGSTATION_DEPENDENCIES += weston
REGSTATION_POST_INSTALL_TARGET_HOOKS += REGSTATION_WAYLAND_WESTON
endif

define REGSTATION_WAYLAND_WESTON
	$(INSTALL) -D -m 0644 $(REGSTATION_PKGDIR)/wayland/weston/weston.ini		$(TARGET_DIR)/etc/xdg/weston/weston.ini
	$(INSTALL) -D -m 0755 $(REGSTATION_PKGDIR)/wayland/weston/weston-launch	$(TARGET_DIR)/usr/bin/weston-launch
endef

define REGSTATION_BOOT
	$(INSTALL) -D -m 0755 $(REGSTATION_PKGDIR)/S31regstation $(TARGET_DIR)/etc/init.d/S31regstation
	$(INSTALL) -D -m 0755 $(REGSTATION_PKGDIR)/regstation-standalone $(TARGET_DIR)/usr/bin/regstation-standalone
	sed -i -e 's;%REGSTATION_PREFIX%;${REGSTATION_PREFIX};g' \
		-e 's;%REGSTATION_CMD%;${REGSTATION_CMD};g' \
		-e 's;%REGSTATION_ARGS%;${REGSTATION_ARGS};g' \
		-e 's;%REGSTATION_POSTFIX%;${REGSTATION_POSTFIX};g' \
		$(TARGET_DIR)/usr/bin/regstation-standalone
	sed -i -e 's;%REGSTATION_PREFIX%;${REGSTATION_PREFIX};g' \
		-e 's;%REGSTATION_CMD%;${REGSTATION_CMD};g' \
		-e 's;%REGSTATION_ARGS%;${REGSTATION_ARGS};g' \
		-e 's;%REGSTATION_POSTFIX%;${REGSTATION_POSTFIX};g' \
		$(TARGET_DIR)/etc/init.d/S31regstation
endef

REGSTATION_POST_EXTRACT_HOOKS += REGSTATION_DOWNLOAD_KEYS
# REGSTATION_OVERRIDE_SRCDIR (make <target>-build REGSTATION_SRCDIR=...) replaces
# download+extract with an rsync, which runs POST_RSYNC instead of POST_EXTRACT.
# Without this the local-tree build would silently get empty scraper /
# retroachievements dev keys.
REGSTATION_POST_RSYNC_HOOKS += REGSTATION_DOWNLOAD_KEYS
REGSTATION_PRE_CONFIGURE_HOOKS += REGSTATION_EXTERNAL_POS
REGSTATION_POST_INSTALL_TARGET_HOOKS += REGSTATION_RESOURCES
REGSTATION_POST_INSTALL_TARGET_HOOKS += REGSTATION_BOOT

# Keep host-side CMake output and CI config out of the rsync — the cross build
# has its own build dir and a host CMakeCache.txt would poison it.
REGSTATION_OVERRIDE_SRCDIR_RSYNC_EXCLUSIONS = \
	--exclude build --exclude build_debug --exclude .github

$(eval $(cmake-package))

else
# Download pre compiled files

REGSTATION_CPU = unknown
ifeq ($(BR2_arm1176jzf_s),y)
	REGSTATION_CPU = arm1176jzf_s
else ifeq ($(BR2_cortex_a7),y)
	REGSTATION_CPU = cortex_a7
else ifeq ($(BR2_cortex_a9),y)
	REGSTATION_CPU = cortex_a9
else ifeq ($(BR2_cortex_a15_a7),y)
	REGSTATION_CPU = cortex_a15_a7
else ifeq ($(BR2_cortex_a17),y)
	REGSTATION_CPU = cortex_a17
else ifeq ($(BR2_cortex_a35),y)
	REGSTATION_CPU = cortex_a35
else ifeq ($(BR2_cortex_a53),y)
	REGSTATION_CPU = cortex_a53
else ifeq ($(BR2_mips_xburst),y)
	REGSTATION_CPU = xburst
else ifeq ($(BR2_cortex_a55),y)
	REGSTATION_CPU = cortex_a55
else ifeq ($(BR2_cortex_a72),y)
	REGSTATION_CPU = cortex_a72
else ifeq ($(BR2_cortex_a72_a53),y)
	REGSTATION_CPU = cortex_a72_a53
else ifeq ($(BR2_cortex_a73_a53),y)
	REGSTATION_CPU = cortex_a73_a53
else ifeq ($(BR2_cortex_a75_a55),y)
	REGSTATION_CPU = cortex_a75_a55
else ifeq ($(BR2_cortex_a76),y)
	REGSTATION_CPU = cortex_a76
else ifeq ($(BR2_cortex_a76_a55),y)
	REGSTATION_CPU = cortex_a76_a55
else ifeq ($(BR2_ARM_CPU_ARMV9A),y) # TODO
	REGSTATION_CPU = cortex_a76_a55
else ifeq ($(BR2_riscv),y)
	REGSTATION_CPU = riscv
else ifeq ($(BR2_saphira),y)
	REGSTATION_CPU = saphira
else ifeq ($(BR2_x86_x86_64_v3),y)
	REGSTATION_CPU = x86_64_v3
else ifeq ($(BR2_x86_64),y)
	REGSTATION_CPU = x86_64
endif

REGSTATION_SHORT_VERSION := $(shell printf '%s' "$(REGSTATION_VERSION)" | cut -c1-7)
REGSTATION_SITE = https://github.com/REG-Linux/REG-Station-binaries/releases/download/$(REGSTATION_SHORT_VERSION)
REGSTATION_SOURCE = regstation-$(REGSTATION_SHORT_VERSION)-$(REGSTATION_CPU).tar.xz
# Paths inside the archive (target/...), after the leading directory is stripped
REGSTATION_LICENSE_FILES = usr/share/regstation/LICENSE usr/share/regstation/THIRD_PARTY_LICENSES

define REGSTATION_INSTALL_TARGET_CMDS
	# extract precompiled files
	tar xvf $(DL_DIR)/$(REGSTATION_DL_SUBDIR)/$(REGSTATION_SOURCE) -C $(TARGET_DIR)/../
endef

$(eval $(generic-package))
endif
