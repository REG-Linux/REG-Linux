################################################################################
#
# CORSIXTH
#
################################################################################

CORSIXTH_VERSION = v0.70.1
CORSIXTH_SITE = $(call github,CorsixTH,CorsixTH,$(CORSIXTH_VERSION))
CORSIXTH_DEPENDENCIES = sdl2 sdl2_image sdl2_mixer ffmpeg libcurl
CORSIXTH_DEPENDENCIES += lua luafilesystem lpeg luasocket luasec

ifeq ($(BR2_PACKAGE_RTMIDI),y)
CORSIXTH_CONF_OPTS += -DWITH_MIDI_DEVICE=ON
CORSIXTH_DEPENDENCIES += rtmidi
else
CORSIXTH_CONF_OPTS += -DWITH_MIDI_DEVICE=OFF
endif

$(eval $(cmake-package))
