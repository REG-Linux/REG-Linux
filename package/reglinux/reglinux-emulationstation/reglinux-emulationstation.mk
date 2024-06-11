################################################################################
#
# REG-emulationstation
#
################################################################################
# Last update: Commits on Jun 4, 2024
REGLINUX_EMULATIONSTATION_VERSION = c5ae14e271a9184342541d7998b3d08b6dacdacc
REGLINUX_EMULATIONSTATION_TOKEN = $(shell cat /build/gh_token)
REGLINUX_EMULATIONSTATION_SITE = https://$(REGLINUX_EMULATIONSTATION_TOKEN)@github.com/REG-Linux/REG-ES
REGLINUX_EMULATIONSTATION_SITE_METHOD = git
REGLINUX_EMULATIONSTATION_LICENSE = MIT
REGLINUX_EMULATIONSTATION_GIT_SUBMODULES = YES
REGLINUX_EMULATIONSTATION_LICENSE = MIT, Apache-2.0
REGLINUX_EMULATIONSTATION_DEPENDENCIES = sdl2 sdl2_mixer ffmpeg libyuv libfreeimage freetype alsa-lib libcurl rapidjson batocera-es-system host-gettext

# REG investigate this, looks like an old "hack" we should remove/avoid
# Pass arch (uppercase) as compiler define
REGLINUX_EMULATIONSTATION_CONF_OPTS += -DCMAKE_CXX_FLAGS=-D$(call UPPERCASE,$(BATOCERA_SYSTEM_ARCH))

# Always build with "batocera" special code
REGLINUX_EMULATIONSTATION_CONF_OPTS += -DBATOCERA=ON

# Debug build settings + install in staging
ifeq ($(BR2_PACKAGE_BATOCERA_DEV)$(BR2_PACKAGE_BATOCERA_DEBUG),y)
REGLINUX_EMULATIONSTATION_INSTALL_STAGING = YES
REGLINUX_EMULATIONSTATION_CONF_OPTS += -DCMAKE_BUILD_TYPE=Debug
#REGLINUX_EMULATIONSTATION_OVERRIDE_SRCDIR = /sources/batocera-emulationstation
endif

# GLM math configuration
REGLINUX_EMULATIONSTATION_CONF_OPTS += -DGLM_ENABLE_CXX_20=ON
REGLINUX_EMULATIONSTATION_CONF_OPTS += -DGLM_ENABLE_FAST_MATH=ON
# SSE2 to AVX2 for x86_64_v3
ifeq ($(BR2_x86_64_v3),y)
REGLINUX_EMULATIONSTATION_CONF_OPTS += -DGLM_ENABLE_SIMD_SSE2=ON
REGLINUX_EMULATIONSTATION_CONF_OPTS += -DGLM_ENABLE_SIMD_SSE3=ON
REGLINUX_EMULATIONSTATION_CONF_OPTS += -DGLM_ENABLE_SIMD_SSSE3=ON
REGLINUX_EMULATIONSTATION_CONF_OPTS += -DGLM_ENABLE_SIMD_SSE4_1=ON
REGLINUX_EMULATIONSTATION_CONF_OPTS += -DGLM_ENABLE_SIMD_SSE4_2=ON
REGLINUX_EMULATIONSTATION_CONF_OPTS += -DGLM_ENABLE_SIMD_AVX=ON
REGLINUX_EMULATIONSTATION_CONF_OPTS += -DGLM_ENABLE_SIMD_AVX2=ON
# SSE2 only for x86_64 baseline
else ifeq ($(BR2_x86_64),y)
REGLINUX_EMULATIONSTATION_CONF_OPTS += -DGLM_ENABLE_SIMD_SSE2=ON
else ifeq ($(BR2_arm)$(BR2_aarch64),y)
# NEON for ARM/AArch64, except for rpi0/1
ifneq ($(BR2_arm1176jzf_s),y)
REGLINUX_EMULATIONSTATION_CONF_OPTS += -DGLM_TEST_ENABLE_SIMD_NEON=ON
endif
endif

ifeq ($(BR2_PACKAGE_HAS_LIBMALI),y)
REGLINUX_EMULATIONSTATION_DEPENDENCIES += libmali
REGLINUX_EMULATIONSTATION_CONF_OPTS += -DCMAKE_EXE_LINKER_FLAGS=-lmali -DCMAKE_SHARED_LINKER_FLAGS=-lmali
endif

# OpenGL desktop vs GLES 2.0 renderer
ifeq ($(BR2_PACKAGE_HAS_LIBGL),y)
REGLINUX_EMULATIONSTATION_CONF_OPTS += -DGL=ON
else ifeq ($(BR2_PACKAGE_HAS_LIBGLES),y)
REGLINUX_EMULATIONSTATION_CONF_OPTS += -DGLES2=ON
endif

# Text-to-speech for visually impaired people
ifeq ($(BR2_PACKAGE_ESPEAK),y)
REGLINUX_EMULATIONSTATION_CONF_OPTS += -DENABLE_TTS=ON
REGLINUX_EMULATIONSTATION_DEPENDENCIES += espeak
endif

# No Kodi
REGLINUX_EMULATIONSTATION_CONF_OPTS += -DDISABLE_KODI=ON

# Enable Pulse only if we are not using the ALSA stack
ifeq ($(BR2_PACKAGE_BATOCERA_AUDIO_ALSA),y)
REGLINUX_EMULATIONSTATION_CONF_OPTS += -DENABLE_PULSE=OFF
else
REGLINUX_EMULATIONSTATION_CONF_OPTS += -DENABLE_PULSE=ON
endif

# Enable file manager if we have X
ifeq ($(BR2_PACKAGE_REGLINUX_XORGAPPS),y)
REGLINUX_EMULATIONSTATION_CONF_OPTS += -DENABLE_FILEMANAGER=ON
else
REGLINUX_EMULATIONSTATION_CONF_OPTS += -DENABLE_FILEMANAGER=OFF
endif

# Enable or disable FFMPEG depending on platform
ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_BCM2835)$(BR2_PACKAGE_BATOCERA_TARGET_RK3128)$(BR2_PACKAGE_BATOCERA_TARGET_JZ4770),y)
REGLINUX_EMULATIONSTATION_CONF_OPTS += -DUSE_FFMPEG=OFF
else
REGLINUX_EMULATIONSTATION_CONF_OPTS += -DUSE_FFMPEG=ON
endif

# Scraping keys
REGLINUX_EMULATIONSTATION_KEY_SCREENSCRAPER_DEV_LOGIN=$(shell grep -E '^SCREENSCRAPER_DEV_LOGIN=' $(BR2_EXTERNAL_BATOCERA_PATH)/package/reglinux/reglinux-emulationstation/keys.txt | cut -d = -f 2-)
REGLINUX_EMULATIONSTATION_KEY_GAMESDB_APIKEY=$(shell grep -E '^GAMESDB_APIKEY=' $(BR2_EXTERNAL_BATOCERA_PATH)/package/reglinux/reglinux-emulationstation/keys.txt | cut -d = -f 2-)
REGLINUX_EMULATIONSTATION_KEY_CHEEVOS_DEV_LOGIN=$(shell grep -E '^CHEEVOS_DEV_LOGIN=' $(BR2_EXTERNAL_BATOCERA_PATH)/package/reglinux/reglinux-emulationstation/keys.txt | cut -d = -f 2-)
REGLINUX_EMULATIONSTATION_KEY_HFS_DEV_LOGIN=$(shell grep -E '^HFS_DEV_LOGIN=' $(BR2_EXTERNAL_BATOCERA_PATH)/package/reglinux/reglinux-emulationstation/keys.txt | cut -d = -f 2-)

ifneq ($(REGLINUX_EMULATIONSTATION_KEY_SCREENSCRAPER_DEV_LOGIN),)
REGLINUX_EMULATIONSTATION_CONF_OPTS += "-DSCREENSCRAPER_DEV_LOGIN=$(REGLINUX_EMULATIONSTATION_KEY_SCREENSCRAPER_DEV_LOGIN)"
endif
ifneq ($(REGLINUX_EMULATIONSTATION_KEY_GAMESDB_APIKEY),)
REGLINUX_EMULATIONSTATION_CONF_OPTS += "-DGAMESDB_APIKEY=$(REGLINUX_EMULATIONSTATION_KEY_GAMESDB_APIKEY)"
endif
ifneq ($(REGLINUX_EMULATIONSTATION_KEY_CHEEVOS_DEV_LOGIN),)
REGLINUX_EMULATIONSTATION_CONF_OPTS += "-DCHEEVOS_DEV_LOGIN=$(REGLINUX_EMULATIONSTATION_KEY_CHEEVOS_DEV_LOGIN)"
endif
ifneq ($(REGLINUX_EMULATIONSTATION_KEY_HFS_DEV_LOGIN),)
REGLINUX_EMULATIONSTATION_CONF_OPTS += "-DHFS_DEV_LOGIN=$(REGLINUX_EMULATIONSTATION_KEY_HFS_DEV_LOGIN)"
endif

# REG investigate this, might cause game launching delays
# disabling cec. causing perf issue on init/deinit
#ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RK3128),y)
REGLINUX_EMULATIONSTATION_CONF_OPTS += -DCEC=OFF
#else
#REGLINUX_EMULATIONSTATION_CONF_OPTS += -DCEC=ON
#endif

# Translations
define REGLINUX_EMULATIONSTATION_EXTERNAL_POS
	cp $(STAGING_DIR)/usr/share/batocera-es-system/es_external_translations.h $(STAGING_DIR)/usr/share/batocera-es-system/es_keys_translations.h $(@D)/es-app/src
	for P in $(STAGING_DIR)/usr/share/batocera-es-system/locales/*; do if test -e $$P/batocera-es-system.po; then cp $(@D)/locale/lang/$$(basename $$P)/LC_MESSAGES/emulationstation2.po $(@D)/locale/lang/$$(basename $$P)/LC_MESSAGES/emulationstation2.po.tmp && $(HOST_DIR)/bin/msgcat $(@D)/locale/lang/$$(basename $$P)/LC_MESSAGES/emulationstation2.po.tmp $$P/batocera-es-system.po > $(@D)/locale/lang/$$(basename $$P)/LC_MESSAGES/emulationstation2.po; fi; done
endef

# Resourrces
define REGLINUX_EMULATIONSTATION_RESOURCES
	$(INSTALL) -m 0755 -d $(TARGET_DIR)/usr/share/emulationstation/resources/help
	$(INSTALL) -m 0755 -d $(TARGET_DIR)/usr/share/emulationstation/resources/flags
	$(INSTALL) -m 0755 -d $(TARGET_DIR)/usr/share/emulationstation/resources/battery
	$(INSTALL) -m 0755 -d $(TARGET_DIR)/usr/share/emulationstation/resources/services
	$(INSTALL) -m 0644 -D $(@D)/resources/*.* $(TARGET_DIR)/usr/share/emulationstation/resources
	$(INSTALL) -m 0644 -D $(@D)/resources/help/*.* $(TARGET_DIR)/usr/share/emulationstation/resources/help
	$(INSTALL) -m 0644 -D $(@D)/resources/flags/*.* $(TARGET_DIR)/usr/share/emulationstation/resources/flags
	$(INSTALL) -m 0644 -D $(@D)/resources/battery/*.* $(TARGET_DIR)/usr/share/emulationstation/resources/battery
	$(INSTALL) -m 0644 -D $(@D)/resources/services/*.* $(TARGET_DIR)/usr/share/emulationstation/resources/services

	# es_input.cfg
	mkdir -p $(TARGET_DIR)/usr/share/batocera/datainit/system/configs/emulationstation
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/reglinux/reglinux-emulationstation/controllers/es_input.cfg \
		$(TARGET_DIR)/usr/share/batocera/datainit/system/configs/emulationstation

	# hooks
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/reglinux/reglinux-emulationstation/batocera-preupdate-gamelists-hook $(TARGET_DIR)/usr/bin/
endef

### S31emulationstation
# default for most of architectures
REGLINUX_EMULATIONSTATION_PREFIX = SDL_NOMOUSE=1
REGLINUX_EMULATIONSTATION_CMD = emulationstation-standalone
REGLINUX_EMULATIONSTATION_ARGS = $${EXTRA_OPTS}
REGLINUX_EMULATIONSTATION_POSTFIX = \&

## on Wayland sway runs ES
ifeq ($(BR2_PACKAGE_REGLINUX_SWAY),y)
REGLINUX_EMULATIONSTATION_DEPENDENCIES += sway
REGLINUX_EMULATIONSTATION_POST_INSTALL_TARGET_HOOKS += REGLINUX_EMULATIONSTATION_WAYLAND_SWAY
endif

define REGLINUX_EMULATIONSTATION_WAYLAND_SWAY
	$(INSTALL) -D -m 0755 $(BR2_EXTERNAL_BATOCERA_PATH)/package/reglinux/reglinux-emulationstation/wayland/sway/config		$(TARGET_DIR)/etc/sway/config
	$(INSTALL) -D -m 0755 $(BR2_EXTERNAL_BATOCERA_PATH)/package/reglinux/reglinux-emulationstation/wayland/sway/launchconfig	$(TARGET_DIR)/etc/sway/launchconfig
endef

define REGLINUX_EMULATIONSTATION_BOOT
	$(INSTALL) -D -m 0755 $(BR2_EXTERNAL_BATOCERA_PATH)/package/reglinux/reglinux-emulationstation/S31emulationstation $(TARGET_DIR)/etc/init.d/S31emulationstation
	$(INSTALL) -D -m 0755 $(BR2_EXTERNAL_BATOCERA_PATH)/package/reglinux/reglinux-emulationstation/emulationstation-standalone $(TARGET_DIR)/usr/bin/emulationstation-standalone
	sed -i -e 's;%REGLINUX_EMULATIONSTATION_PREFIX%;${REGLINUX_EMULATIONSTATION_PREFIX};g' \
		-e 's;%REGLINUX_EMULATIONSTATION_CMD%;${REGLINUX_EMULATIONSTATION_CMD};g' \
		-e 's;%REGLINUX_EMULATIONSTATION_ARGS%;${REGLINUX_EMULATIONSTATION_ARGS};g' \
		-e 's;%REGLINUX_EMULATIONSTATION_POSTFIX%;${REGLINUX_EMULATIONSTATION_POSTFIX};g' \
		$(TARGET_DIR)/usr/bin/emulationstation-standalone
	sed -i -e 's;%REGLINUX_EMULATIONSTATION_PREFIX%;${REGLINUX_EMULATIONSTATION_PREFIX};g' \
		-e 's;%REGLINUX_EMULATIONSTATION_CMD%;${REGLINUX_EMULATIONSTATION_CMD};g' \
		-e 's;%REGLINUX_EMULATIONSTATION_ARGS%;${REGLINUX_EMULATIONSTATION_ARGS};g' \
		-e 's;%REGLINUX_EMULATIONSTATION_POSTFIX%;${REGLINUX_EMULATIONSTATION_POSTFIX};g' \
		$(TARGET_DIR)/etc/init.d/S31emulationstation
endef

REGLINUX_EMULATIONSTATION_PRE_CONFIGURE_HOOKS += REGLINUX_EMULATIONSTATION_EXTERNAL_POS
REGLINUX_EMULATIONSTATION_POST_INSTALL_TARGET_HOOKS += REGLINUX_EMULATIONSTATION_RESOURCES
REGLINUX_EMULATIONSTATION_POST_INSTALL_TARGET_HOOKS += REGLINUX_EMULATIONSTATION_BOOT

$(eval $(cmake-package))
