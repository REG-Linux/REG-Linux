################################################################################
#
# CORSIXTH
#
################################################################################

CORSIXTH_VERSION = v0.69.2
CORSIXTH_SITE = $(call github,CorsixTH,CorsixTH,$(CORSIXTH_VERSION))
CORSIXTH_DEPENDENCIES = sdl2 sdl2_image sdl2_mixer ffmpeg libcurl
CORSIXTH_DEPENDENCIES += lua luafilesystem lpeg luasocket luasec

$(eval $(cmake-package))
