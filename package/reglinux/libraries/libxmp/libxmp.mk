################################################################################
#
# LIBXMP
#
################################################################################

LIBXMP_VERSION = libxmp-4.6.1
LIBXMP_SITE =  $(call github,libxmp,libxmp,$(LIBXMP_VERSION))
LIBXMP_INSTALL_STAGING = YES
LIBXMP_AUTORECONF = YES
LIBXMP_DEPENDENCIES = host-pkgconf
LIBXMP_LICENSE = MIT

$(eval $(autotools-package))
