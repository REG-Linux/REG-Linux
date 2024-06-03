################################################################################
#
# Oricutron - Oric computers emulator
#
################################################################################
# Version.: Release on Nov 19, 2023
ORICUTRON_VERSION = V1_2_5
ORICUTRON_SITE = https://github.com/pete-gordon/oricutron
ORICUTRON_SITE_METHOD=git
ORICUTRON_LICENSE = GPLv3
ORICUTRON_DEPENDENCIES = sdl2

ORICUTRON_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release -DUSE_SDL2=ON

$(eval $(cmake-package))
