################################################################################
#
# libplacebo
#
################################################################################

LIBPLACEBO_VERSION = v7.351.0
LIBPLACEBO_SITE = https://github.com/haasn/libplacebo
LIBPLACEBO_SITE_METHOD=git
LIBPLACEBO_LICENSE = LGPL-2.1
LIBPLACEBO_LICENSE_FILES = LICENSE
LIBPLACEBO_GIT_SUBMODULES = YES

#LIBPLACEBO_DEPENDENCIES = libdrm

LIBPLACEBO_INSTALL_STAGING = YES

$(eval $(meson-package))
