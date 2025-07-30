################################################################################
#
# CORSIXTH
#
################################################################################

CORSIXTH_VERSION = v0.69.0
CORSIXTH_SITE = $(call github,CorsixTH,CorsixTH,$(CORSIXTH_VERSION))
CORSIXTH_DEPENDENCIES = sdl2 sdl2_image sdl2_mixer ffmpeg libcurl
CORSIXTH_DEPENDENCIES += lua luafilesystem lpeg luasocket luasec

define CORSIXTH_INSTALL_EVMAPY
        # evmap config
        mkdir -p $(TARGET_DIR)/usr/share/evmapy
        cp $(BR2_EXTERNAL_REGLINUX_PATH)/package/ports/corsixth/corsixth.keys $(TARGET_DIR)/usr/share/evmapy
endef

CORSIXTH_POST_INSTALL_TARGET_HOOKS += CORSIXTH_INSTALL_EVMAPY

$(eval $(cmake-package))
