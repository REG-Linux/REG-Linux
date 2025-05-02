################################################################################
#
# libenet
#
################################################################################

LIBENET_VERSION = v1.3.18
LIBENET_SITE = $(call github,lsalzman,enet,$(LIBENET_VERSION))
LIBENET_INSTALL_STAGING = YES
LIBENET_AUTORECONF = YES
LIBENET_DEPENDENCIES = host-pkgconf

$(eval $(autotools-package))
