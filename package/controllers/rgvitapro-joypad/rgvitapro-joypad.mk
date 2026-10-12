################################################################################
#
# rgvitapro-joypad — RG Vita Pro GPIO joypad driver
#
################################################################################

RGVITAPRO_JOYPAD_VERSION = 1.0
RGVITAPRO_JOYPAD_SITE = $(RGVITAPRO_JOYPAD_PKGDIR)/src
RGVITAPRO_JOYPAD_SITE_METHOD = local
RGVITAPRO_JOYPAD_LICENSE = GPL-2.0+

RGVITAPRO_JOYPAD_MODULE_MAKE_OPTS = \
	CONFIG_RGVITAPRO_JOYPAD=m

$(eval $(kernel-module))
$(eval $(generic-package))
