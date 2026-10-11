################################################################################
#
# Yamagi Quake 2
#
################################################################################

YQUAKE2_VERSION = 8.50
YQUAKE2_DEPENDENCIES += sdl2 yquake2-client
YQUAKE2_DEPENDENCIES += yquake2-xatrix yquake2-rogue yquake2-ctf yquake2-zaero

ifeq ($(BR2_PACKAGE_YQUAKE2_REF_VK),y)
YQUAKE2_DEPENDENCIES += yquake2-ref-vk
endif

$(eval $(virtual-package))
