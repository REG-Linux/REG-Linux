################################################################################
#
# sndio-compat
#
# libsndio.so.7 for the glibc sidecar, on ALSA (so through the pulse plugin,
# like the rest of the sidecar's audio). Library only, no sndiod.
#
################################################################################

SNDIO_COMPAT_VERSION = 1.9.0
SNDIO_COMPAT_SITE = https://sndio.org
SNDIO_COMPAT_SOURCE = sndio-$(SNDIO_COMPAT_VERSION).tar.gz
SNDIO_COMPAT_LICENSE = ISC
SNDIO_COMPAT_DEPENDENCIES = alsa-lib

# Its own configure script: no --host, the compiler comes from the arguments
define SNDIO_COMPAT_CONFIGURE_CMDS
	cd $(@D) && ./configure \
		--prefix=/usr \
		--enable-alsa \
		--disable-sun \
		--disable-rmidi \
		--disable-umidi \
		--without-libbsd \
		CC="$(TARGET_CC)" \
		CFLAGS="$(TARGET_CFLAGS)" \
		LDFLAGS="$(TARGET_LDFLAGS)"
endef

define SNDIO_COMPAT_BUILD_CMDS
	$(TARGET_MAKE_ENV) $(MAKE) -C $(@D)/libsndio CC="$(TARGET_CC)"
endef

define SNDIO_COMPAT_INSTALL_TARGET_CMDS
	cp -a $(@D)/libsndio/libsndio.so.7* $(TARGET_DIR)/usr/lib/
endef

$(eval $(generic-package))
