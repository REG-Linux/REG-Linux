################################################################################
#
# dosbox-x
#
################################################################################

DOSBOX_X_VERSION = dosbox-x-v2025.12.01
DOSBOX_X_SITE = $(call github,joncampbell123,dosbox-x,$(DOSBOX_X_VERSION))
DOSBOX_X_DEPENDENCIES = sdl2 sdl2_net zlib libpng libogg libvorbis linux-headers
DOSBOX_X_LICENSE = GPLv2

ifeq ($(BR2_PACKAGE_FLUIDSYNTH),y)
DOSBOX_X_DEPENDENCIES += fluidsynth
DOSBOX_X_CONF_OPTS += --enable-fluidsynth
else
DOSBOX_X_CONF_OPTS += --disable-fluidsynth
endif

# Extra configure options for Dosbox-X
DOSBOX_X_CONF_OPTS += \
	--enable-core-inline \
	--enable-dynrec \
	--enable-unaligned_memory \
	--prefix=/usr \
	--disable-sdl \
	--enable-sdl2 \
	--with-sdl2-prefix="$(STAGING_DIR)/usr"

# Linker flags required for Vorbis and Ogg support
DOSBOX_X_CONF_ENV += LIBS="-lvorbisfile -lvorbis -logg"

define DOSBOX_X_CONFIGURE_CONFIG
	mkdir -p $(TARGET_DIR)/usr/share/reglinux/datainit/system/configs/dosbox
	cp -rf $(@D)/dosbox-x.reference.conf \
		$(TARGET_DIR)/usr/share/reglinux/datainit/system/configs/dosbox/dosboxx.conf
endef

DOSBOX_X_POST_INSTALL_TARGET_HOOKS += DOSBOX_X_CONFIGURE_CONFIG

# Force autoreconf because the repository does not ship a pre-generated configure script
DOSBOX_X_AUTORECONF = YES

$(eval $(autotools-package))
