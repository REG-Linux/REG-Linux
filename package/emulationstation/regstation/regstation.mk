################################################################################
#
# REG-Station
#
################################################################################

# WIP branch
REGSTATION_VERSION = 5b99261147c1ba3469bcb43a6a626e206640fc0c
REGSTATION_TOKEN = $(shell cat /build/gh_token)
REGSTATION_SITE = https://$(REGSTATION_TOKEN)@github.com/REG-Linux/REG-ES
REGSTATION_SITE_METHOD = git
REGSTATION_LICENSE = MIT
REGSTATION_GIT_SUBMODULES = YES
REGSTATION_LICENSE = MIT, Apache-2.0
REGSTATION_DEPENDENCIES = sdl3 sdl3_mixer libyuv libfreeimage
REGSTATION_DEPENDENCIES += freetype alsa-lib libcurl rapidjson libarchive
REGSTATION_DEPENDENCIES += lunasvg pugixml host-gettext
REGSTATION_DEPENDENCIES += es-system gamecontrollerdb

REGSTATION_SUPPORTS_IN_SOURCE_BUILD = NO
REGSTATION_PATH = $(BR2_EXTERNAL_REGLINUX_PATH)/package/emulationstation/regstation

# REG investigate this, looks like an old "hack" we should remove/avoid
# Pass arch (uppercase) as compiler define
REGSTATION_CONF_OPTS += -DCMAKE_CXX_FLAGS=-D$(call UPPERCASE,$(REGLINUX_SYSTEM_ARCH))

# Always build with "batocera" special code
REGSTATION_CONF_OPTS += -DBATOCERA=ON

# File manager
REGSTATION_CONF_OPTS += -DENABLE_FILEMANAGER=OFF

# Force to use es-ffmpeg LGPL
REGSTATION_CONF_OPTS += -DFFMPEG_DIR="$(STAGING_DIR)/usr/lib/es-ffmpeg"

# Debug build settings + install in staging
ifeq ($(BR2_ENABLE_DEBUG),y)
REGSTATION_INSTALL_STAGING = YES
REGSTATION_CONF_OPTS += -DCMAKE_BUILD_TYPE=Debug
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

# Text-to-speech for visually impaired people
ifeq ($(BR2_PACKAGE_ESPEAK),y)
REGSTATION_CONF_OPTS += -DENABLE_TTS=ON
REGSTATION_DEPENDENCIES += espeak
endif

# No Kodi
REGSTATION_CONF_OPTS += -DDISABLE_KODI=ON

# Enable Pulse only if we are not using the ALSA stack
ifeq ($(BR2_PACKAGE_BATOCERA_AUDIO_ALSA),y)
REGSTATION_CONF_OPTS += -DENABLE_PULSE=OFF
else
REGSTATION_CONF_OPTS += -DENABLE_PULSE=ON
REGSTATION_DEPENDENCIES += pulseaudio
endif

# Enable or disable FFMPEG depending on platform
ifeq ($(BR2_PACKAGE_ES_FFMPEG),y)
REGSTATION_CONF_OPTS += -DUSE_FFMPEG=ON
REGSTATION_DEPENDENCIES += es-ffmpeg
else
REGSTATION_CONF_OPTS += -DUSE_FFMPEG=OFF
endif

# Scraping keys
REGSTATION_CONF_OPTS += "-DSCREENSCRAPER_DEV_LOGIN=$(shell grep -m 1 -E '^SCREENSCRAPER_DEV_LOGIN=' $(@D)/keys.txt | cut -d = -f 2-)"
REGSTATION_CONF_OPTS += "-DGAMESDB_APIKEY=$(shell grep -m 1 -E '^GAMESDB_APIKEY=' $(@D)/keys.txt | cut -d = -f 2-)"
REGSTATION_CONF_OPTS += "-DCHEEVOS_DEV_LOGIN=$(shell grep -m 1 -E '^CHEEVOS_DEV_LOGIN=' $(@D)/keys.txt | cut -d = -f 2-)"
REGSTATION_CONF_OPTS += "-DHFS_DEV_LOGIN=$(shell grep -m 1 -E '^HFS_DEV_LOGIN=' $(@D)/keys.txt | cut -d = -f 2-)"

# REG investigate this, might cause game launching delays
# disabling cec. causing perf issue on init/deinit
#ifeq ($(BR2_PACKAGE_SYSTEM_TARGET_RK3128),y)
REGSTATION_CONF_OPTS += -DCEC=OFF
#else
#REGSTATION_CONF_OPTS += -DCEC=ON
#endif

define REGSTATION_DOWNLOAD_KEYS
	# Download scrapper and retroachievements developer keys
	wget --header="Authorization: token $(REGSTATION_TOKEN)" -O $(@D)/keys.txt "https://raw.githubusercontent.com/REG-Linux/keys/main/key.txt" || true
endef

# Translations and LogLevel define
define REGSTATION_EXTERNAL_POS
#	cp $(STAGING_DIR)/usr/share/es-system/es_external_translations.h $(STAGING_DIR)/usr/share/es-system/es_keys_translations.h $(@D)/es-app/src
#	for P in $(STAGING_DIR)/usr/share/es-system/locales/*; do if test -e $$P/es-system.po; then cp $(@D)/locale/lang/$$(basename $$P)/LC_MESSAGES/emulationstation2.po $(@D)/locale/lang/$$(basename $$P)/LC_MESSAGES/emulationstation2.po.tmp && $(HOST_DIR)/bin/msgcat $(@D)/locale/lang/$$(basename $$P)/LC_MESSAGES/emulationstation2.po.tmp $$P/es-system.po > $(@D)/locale/lang/$$(basename $$P)/LC_MESSAGES/emulationstation2.po; fi; done

	# Hijack .po copy to adjust LogLevel
#	if test "$(BR2_ENABLE_DEBUG)" = "y" ; then sed -i "s/level \= \"default\"\;/level \= \"error\"\;/" "$(@D)/es-app/src/guis/GuiMenu.cpp"; fi
endef

# Resources
define REGSTATION_RESOURCES
	$(INSTALL) -m 0755 -d $(TARGET_DIR)/usr/share/emulationstation/resources/help
	$(INSTALL) -m 0755 -d $(TARGET_DIR)/usr/share/emulationstation/resources/flags
	$(INSTALL) -m 0755 -d $(TARGET_DIR)/usr/share/emulationstation/resources/battery
	$(INSTALL) -m 0755 -d $(TARGET_DIR)/usr/share/emulationstation/resources/services
	$(INSTALL) -m 0644 -D $(@D)/resources/*.* $(TARGET_DIR)/usr/share/emulationstation/resources
	$(INSTALL) -m 0644 -D $(@D)/resources/help/*.* $(TARGET_DIR)/usr/share/emulationstation/resources/help
	$(INSTALL) -m 0644 -D $(@D)/resources/flags/*.* $(TARGET_DIR)/usr/share/emulationstation/resources/flags
	$(INSTALL) -m 0644 -D $(@D)/resources/battery/*.* $(TARGET_DIR)/usr/share/emulationstation/resources/battery
	$(INSTALL) -m 0644 -D $(@D)/resources/services/*.* $(TARGET_DIR)/usr/share/emulationstation/resources/services

	# hooks
	cp $(REGSTATION_PATH)/batocera-preupdate-gamelists-hook $(TARGET_DIR)/usr/bin/
endef

### S31regstation
# default for most of architectures
REGSTATION_CMD = emulationstation-standalone
REGSTATION_ARGS = $${EXTRA_OPTS}
REGSTATION_POSTFIX = \&

## on Wayland sway runs ES
ifeq ($(BR2_PACKAGE_REGLINUX_SWAY),y)
REGSTATION_DEPENDENCIES += sway
REGSTATION_POST_INSTALL_TARGET_HOOKS += REGSTATION_WAYLAND_SWAY
endif

define REGSTATION_WAYLAND_SWAY
	$(INSTALL) -D -m 0755 $(REGSTATION_PATH)/wayland/sway/04-sway.sh	$(TARGET_DIR)/etc/profile.d/04-sway.sh
	$(INSTALL) -D -m 0755 $(REGSTATION_PATH)/wayland/sway/config		$(TARGET_DIR)/etc/sway/config
	$(INSTALL) -D -m 0755 $(REGSTATION_PATH)/wayland/sway/launchconfig	$(TARGET_DIR)/etc/sway/launchconfig
endef

define REGSTATION_BOOT
	$(INSTALL) -D -m 0755 $(REGSTATION_PATH)/S31regstation $(TARGET_DIR)/etc/init.d/S31regstation
	$(INSTALL) -D -m 0755 $(REGSTATION_PATH)/emulationstation-standalone $(TARGET_DIR)/usr/bin/emulationstation-standalone
	if test "$(BR2_PACKAGE_SYSTEM_TARGET_CHA)" = "y" ; then patch "$(TARGET_DIR)/usr/bin/emulationstation-standalone" < "$(REGSTATION_PATH)/force-CHA1-to-P1-patch-for-CHA"; fi
	sed -i -e 's;%REGSTATION_PREFIX%;${REGSTATION_PREFIX};g' \
		-e 's;%REGSTATION_CMD%;${REGSTATION_CMD};g' \
		-e 's;%REGSTATION_ARGS%;${REGSTATION_ARGS};g' \
		-e 's;%REGSTATION_POSTFIX%;${REGSTATION_POSTFIX};g' \
		$(TARGET_DIR)/usr/bin/emulationstation-standalone
	sed -i -e 's;%REGSTATION_PREFIX%;${REGSTATION_PREFIX};g' \
		-e 's;%REGSTATION_CMD%;${REGSTATION_CMD};g' \
		-e 's;%REGSTATION_ARGS%;${REGSTATION_ARGS};g' \
		-e 's;%REGSTATION_POSTFIX%;${REGSTATION_POSTFIX};g' \
		$(TARGET_DIR)/etc/init.d/S31regstation
endef

REGSTATION_POST_EXTRACT_HOOKS += REGSTATION_DOWNLOAD_KEYS
REGSTATION_PRE_CONFIGURE_HOOKS += REGSTATION_EXTERNAL_POS
REGSTATION_POST_INSTALL_TARGET_HOOKS += REGSTATION_RESOURCES
REGSTATION_POST_INSTALL_TARGET_HOOKS += REGSTATION_BOOT

$(eval $(cmake-package))
