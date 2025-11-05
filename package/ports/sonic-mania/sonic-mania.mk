################################################################################
#
# sonic-mania
#
################################################################################
# Version: Release on Nov 1, 2025
SONIC_MANIA_VERSION = v1.1.1
SONIC_MANIA_SITE = https://github.com/RSDKModding/Sonic-Mania-Decompilation.git
SONIC_MANIA_SITE_METHOD = git
SONIC_MANIA_GIT_SUBMODULES = YES
SONIC_MANIA_LICENSE = Proprietary
SONIC_MANIA_LICENSE_FILE = LICENSE.md

SONIC_MANIA_DEPENDENCIES += libogg libtheora portaudio sdl2

SONIC_MANIA_SUPPORTS_IN_SOURCE_BUILD = NO

SONIC_MANIA_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release
SONIC_MANIA_CONF_OPTS += -DBUILD_SHARED_LIBS=OFF
SONIC_MANIA_CONF_OPTS += -DBUILD_STATIC_LIBS=ON
SONIC_MANIA_CONF_OPTS += -DGAME_STATIC=ON
SONIC_MANIA_CONF_OPTS += -DGAME_INCLUDE_EDITOR=OFF
SONIC_MANIA_CONF_OPTS += -DRETRO_OUTPUT_NAME=sonic-mania
SONIC_MANIA_CONF_OPTS += -DRETRO_SUBSYSTEM=SDL2

define SONIC_MANIA_INSTALL_TARGET_CMDS
	$(INSTALL) -D -m 0755 $(@D)/buildroot-build/dependencies/RSDKv5/sonic-mania \
	    $(TARGET_DIR)/usr/bin/sonic-mania
endef

define SONIC_MANIA_EVMAPY
	mkdir -p $(TARGET_DIR)/usr/share/evmapy
	cp $(BR2_EXTERNAL_REGLINUX_PATH)/package/ports/sonic-mania/sonic-mania.keys \
	    $(TARGET_DIR)/usr/share/evmapy
endef

SONIC_MANIA_POST_INSTALL_TARGET_HOOKS += SONIC_MANIA_EVMAPY

$(eval $(cmake-package))
