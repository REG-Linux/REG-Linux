################################################################################
#
# Free Heroes (of Might and Magic) 2 engine
#
################################################################################

# Release on Nov 9, 2025
FHEROES2_VERSION = 1.1.12
FHEROES2_SITE = $(call github,ihhub,fheroes2,$(FHEROES2_VERSION))
FHEROES2_DEPENDENCIES = sdl2 sdl2_image sdl2_mixer

FHEROES2_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release
FHEROES2_CONF_OPTS += -DBUILD_SHARED_LIBS=OFF
FHEROES2_CONF_OPTS += -DBUILD_STATIC_LIBS=ON

$(eval $(cmake-package))
