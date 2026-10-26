################################################################################
#
# libzip-compat
#
# libzip 1.1 for the glibc sidecar: libzip.so.4, which ports built on Ubuntu
# 18.04 link (1.3 changed it to libzip.so.5). Library only.
#
################################################################################

LIBZIP_COMPAT_VERSION = 1.1.3
LIBZIP_COMPAT_SITE = https://libzip.org/download
LIBZIP_COMPAT_SOURCE = libzip-$(LIBZIP_COMPAT_VERSION).tar.xz
LIBZIP_COMPAT_DL_SUBDIR = libzip
LIBZIP_COMPAT_LICENSE = BSD-3-Clause
LIBZIP_COMPAT_LICENSE_FILES = LICENSE
LIBZIP_COMPAT_DEPENDENCIES = zlib
LIBZIP_COMPAT_CONF_OPTS = --disable-static

define LIBZIP_COMPAT_BUILD_CMDS
	$(TARGET_MAKE_ENV) $(MAKE) -C $(@D)/lib
endef

define LIBZIP_COMPAT_INSTALL_TARGET_CMDS
	cp -a $(@D)/lib/.libs/libzip.so.4* $(TARGET_DIR)/usr/lib/
endef

$(eval $(autotools-package))
