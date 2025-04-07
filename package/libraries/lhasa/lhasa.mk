################################################################################
#
# lhasa
#
################################################################################

LHASA_VERSION = v0.4.0
LHASA_SITE =  $(call github,fragglet,lhasa,$(LHASA_VERSION))
LHASA_INSTALL_STAGING = YES
LHASA_AUTORECONF = YES
LHASA_DEPENDENCIES = host-pkgconf
LHASA_LICENSE = ISC

$(eval $(autotools-package))
