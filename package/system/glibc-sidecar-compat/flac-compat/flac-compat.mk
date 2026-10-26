################################################################################
#
# flac-compat
#
# libFLAC 1.3 for the glibc sidecar: ports built on Ubuntu 20.04/22.04 link
# libFLAC.so.8 (FLAC 1.4 is libFLAC.so.12). Library only.
#
################################################################################

FLAC_COMPAT_VERSION = 1.3.4
FLAC_COMPAT_SITE = https://ftp.osuosl.org/pub/xiph/releases/flac
FLAC_COMPAT_SOURCE = flac-$(FLAC_COMPAT_VERSION).tar.xz
FLAC_COMPAT_DL_SUBDIR = flac
FLAC_COMPAT_LICENSE = Xiph BSD-like
FLAC_COMPAT_LICENSE_FILES = COPYING.Xiph
FLAC_COMPAT_DEPENDENCIES = libogg

# Same as flac: libFLAC crashes with GCC 13+ at -O3
FLAC_COMPAT_CONF_ENV = CFLAGS="-O2"
FLAC_COMPAT_CONF_OPTS = \
	--with-ogg=$(STAGING_DIR)/usr \
	--disable-cpplibs \
	--disable-programs \
	--disable-examples \
	--disable-doxygen-docs \
	--disable-xmms-plugin \
	--disable-stack-smash-protection \
	--disable-static

define FLAC_COMPAT_BUILD_CMDS
	$(TARGET_MAKE_ENV) $(MAKE) -C $(@D)/src/libFLAC
endef

define FLAC_COMPAT_INSTALL_TARGET_CMDS
	cp -a $(@D)/src/libFLAC/.libs/libFLAC.so.8* $(TARGET_DIR)/usr/lib/
endef

$(eval $(autotools-package))
