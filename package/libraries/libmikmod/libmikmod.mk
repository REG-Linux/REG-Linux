################################################################################
#
# libmikmod
#
################################################################################

LIBMIKMOD_VERSION = libmikmod-3.3.13
LIBMIKMOD_SITE = $(call github,sezero,mikmod,$(LIBMIKMOD_VERSION))
LIBMIKMOD_SUBDIR = libmikmod
LIBMIKMOD_LICENSE = LGPL-2.1+
LIBMIKMOD_INSTALL_STAGING = YES

LIBMIKMOD_CONF_OPTS = \
	-DCMAKE_POSITION_INDEPENDENT_CODE=ON \
	-DENABLE_SHARED=OFF \
	-DENABLE_DOC=OFF

$(eval $(cmake-package))
