################################################################################
#
# libxml2-compat
#
# libxml2 2.13 for the glibc sidecar: its soname is libxml2.so.2, the one
# ports link; 2.14 changed it to libxml2.so.16. Library only.
#
################################################################################

LIBXML2_COMPAT_VERSION = 2.13.8
LIBXML2_COMPAT_SITE = https://download.gnome.org/sources/libxml2/2.13
LIBXML2_COMPAT_SOURCE = libxml2-$(LIBXML2_COMPAT_VERSION).tar.xz
LIBXML2_COMPAT_DL_SUBDIR = libxml2
LIBXML2_COMPAT_LICENSE = MIT
LIBXML2_COMPAT_LICENSE_FILES = Copyright
LIBXML2_COMPAT_DEPENDENCIES = zlib

# HTTP and FTP: off by default since 2.13, on in the Ubuntu builds ports link
# (armagetronad calls xmlNanoHTTPRead)
LIBXML2_COMPAT_CONF_OPTS = \
	--with-http \
	--with-ftp \
	--with-zlib=$(STAGING_DIR)/usr \
	--without-lzma \
	--without-icu \
	--without-python \
	--without-debug \
	--with-threads \
	--disable-static

define LIBXML2_COMPAT_BUILD_CMDS
	$(TARGET_MAKE_ENV) $(MAKE) -C $(@D) libxml2.la
endef

define LIBXML2_COMPAT_INSTALL_TARGET_CMDS
	cp -a $(@D)/.libs/libxml2.so.2* $(TARGET_DIR)/usr/lib/
endef

$(eval $(autotools-package))
