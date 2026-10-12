################################################################################
#
# uchardet — encoding auto-detection library
#
################################################################################

UCHARDET_VERSION = v0.0.8
UCHARDET_SITE = https://gitlab.freedesktop.org/uchardet/uchardet/-/archive/$(UCHARDET_VERSION)
UCHARDET_SOURCE = uchardet-$(UCHARDET_VERSION).tar.gz

UCHARDET_LICENSE = MPL-1.1
UCHARDET_INSTALL_STAGING = YES

UCHARDET_CONF_OPTS = \
	-DBUILD_BINARY=OFF \
	-DBUILD_STATIC=OFF

$(eval $(cmake-package))
