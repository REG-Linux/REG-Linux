################################################################################
#
# jazz2-native
#
################################################################################

JAZZ2_NATIVE_VERSION = 3.8.0
JAZZ2_NATIVE_SITE = $(call github,deathkiller,jazz2-native,$(JAZZ2_NATIVE_VERSION))
JAZZ2_NATIVE_LICENSE = GPL-3.0
JAZZ2_NATIVE_LICENSE_FILE = LICENSE

JAZZ2_NATIVE_DEPENDENCIES += sdl2 openal libopenmpt zlib libcurl

JAZZ2_NATIVE_SUPPORTS_IN_SOURCE_BUILD = NO

JAZZ2_NATIVE_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release
JAZZ2_NATIVE_CONF_OPTS += -DBUILD_SHARED_LIBS=OFF
JAZZ2_NATIVE_CONF_OPTS += -DNCINE_LINUX_PACKAGE="jazz2"
JAZZ2_NATIVE_CONF_OPTS += -DNCINE_DOWNLOAD_DEPENDENCIES=OFF

# Always SDL2, never nCine's GLFW backend. nCine maps joysticks itself, from the
# SDL_GAMECONTROLLERCONFIG the launcher hands it, but it applies that mapping to
# whatever button order the backend reports. GLFW numbers buttons by ascending evdev
# code while SDL (and the mappings REG-Linux generates) follow joydev order, which puts
# the 0x120+ gamepad range first and stray codes last -- one BTN_BACK on the Retroid
# Pocket pad shifts every button by one, so A lands on a dead code and the d-pad rotates.
# GLFW also enumerates touchscreens as gamepads, and an untouched panel reads as a stick
# held hard over; SDL2 skips them because udev tags them ID_INPUT_TOUCHSCREEN.
JAZZ2_NATIVE_CONF_OPTS += -DNCINE_PREFERRED_BACKEND=SDL2

ifneq ($(BR2_PACKAGE_XORG7)$(BR2_PACKAGE_HAS_LIBGL),yy)
    JAZZ2_NATIVE_CONF_OPTS += -DNCINE_WITH_OPENGLES=ON
endif

# nCine picks the GLES 3.0 profile by default on ARM Linux (ncine_options.cmake:
# "GLES is the implementation that is actually accelerated there"), which boards
# whose GPU stops at GLES 2.0 cannot provide -- Mali-400/lima on h3 and cha,
# rk3128, the older Broadcom parts. Both of these serve them, and which is
# faster is a property of the hardware, not of the engine:
#
#   -DNCINE_RHI_GL_PROFILE=ES2      render on the GPU through the engine's ES 2.0
#                                   profile (ESSL 100 shaders, no UBOs)
#   -DNCINE_PREFERRED_RHI=Software  rasterize on the CPU, present through
#                                   SDL_Renderer (forces the SDL2 backend, which
#                                   this package already selects above)
#
# Measured in-game on a CHA (quad Cortex-A7 + Mali-400, 1080p): ES2 gives 20-26
# fps on Jazz2 1.24 but only 7-10 on The Christmas Chronicles, and neither
# resolution, lighting resolution nor blur moved it -- the GPU is the wall, not
# fill rate. Software gives 17 and 12 on the same two. So Software is chosen for
# the worst case rather than the best: it gives up the peak on 1.24 to take CC
# from unplayable to playable, which is the difference that matters on a board
# this slow. Swap to -DNCINE_RHI_GL_PROFILE=ES2 to go back to the GPU.
ifneq ($(BR2_PACKAGE_HAS_GLES3),y)
    JAZZ2_NATIVE_CONF_OPTS += -DNCINE_PREFERRED_RHI=Software
endif

$(eval $(cmake-package))
