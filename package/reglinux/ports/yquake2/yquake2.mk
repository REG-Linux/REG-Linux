################################################################################
#
# Yamagi Quake 2
#
################################################################################

YQUAKE2_VERSION = 8.30
YQUAKE2_DEPENDENCIES = sdl2 yquake2-client yquake2-xatrix yquake2-rogue
YQUAKE2_DEPENDENCIES += sdl2 yquake2-ctf yquake2-zaero

$(eval $(virtual-package))
