################################################################################
#
# fontconfig
#
################################################################################
# reglinux - update
FONTCONFIG_VERSION = 2.15.0
FONTCONFIG_SITE = https://www.freedesktop.org/software/fontconfig/release
FONTCONFIG_SOURCE = fontconfig-$(FONTCONFIG_VERSION).tar.xz
# 0001-add-pthread-as-a-dependency-of-a-static-lib.patch
FONTCONFIG_AUTORECONF = YES
FONTCONFIG_INSTALL_STAGING = YES
FONTCONFIG_DEPENDENCIES = freetype expat host-pkgconf host-gperf \
	$(if $(BR2_PACKAGE_UTIL_LINUX_LIBS),util-linux-libs,util-linux) \
	$(TARGET_NLS_DEPENDENCIES)
HOST_FONTCONFIG_DEPENDENCIES = \
	host-freetype host-expat host-pkgconf host-gperf host-util-linux \
	host-gettext
FONTCONFIG_LICENSE = fontconfig license
FONTCONFIG_LICENSE_FILES = COPYING
FONTCONFIG_CPE_ID_VALID = YES

FONTCONFIG_CONF_OPTS = \
	--with-arch=$(GNU_TARGET_NAME) \
	--with-cache-dir=/var/cache/fontconfig \
	--disable-docs

HOST_FONTCONFIG_CONF_OPTS = \
	--disable-static

$(eval $(autotools-package))
$(eval $(host-autotools-package))
