################################################################################
#
# Yamagi Quake 2
#
################################################################################

YQUAKE2_VERSION = 8.41
YQUAKE2_DEPENDENCIES += sdl2 yquake2-client
YQUAKE2_DEPENDENCIES += yquake2-xatrix yquake2-rogue yquake2-ctf yquake2-zaero

$(eval $(virtual-package))
