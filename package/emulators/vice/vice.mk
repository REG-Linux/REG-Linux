################################################################################
#
# vice
#
################################################################################

VICE_VERSION = 3.9
VICE_SOURCE = vice-$(VICE_VERSION).tar.gz
VICE_SITE = https://sourceforge.net/projects/vice-emu/files/releases
VICE_LICENSE = GPLv2
VICE_DEPENDENCIES = sdl2 sdl2_image libcurl host-dos2unix host-xa
VICE_DEPENDENCIES += giflib alsa-lib jpeg

VICE_CONF_OPTS += --disable-option-checking
VICE_CONF_OPTS += --enable-midi
VICE_CONF_OPTS += --without-pulse
VICE_CONF_OPTS += --with-fastsid
VICE_CONF_OPTS += --with-evdev
VICE_CONF_OPTS += --enable-x64
VICE_CONF_OPTS += --enable-arch=yes
VICE_CONF_OPTS += --enable-sdl2ui
VICE_CONF_OPTS += --with-sdlsound
VICE_CONF_OPTS += --disable-hardsid
VICE_CONF_OPTS += --disable-parsid
VICE_CONF_OPTS += --disable-debug-gtk3ui
VICE_CONF_OPTS += --disable-html-docs
VICE_CONF_OPTS += --disable-pdf-docs
# TODO handle properly these
VICE_CONF_OPTS += --with-alsa
VICE_CONF_OPTS += --with-jpeg
VICE_CONF_OPTS += --with-gif
# needs old ffmpeg 4.x
#VICE_CONF_OPTS += --enable-ffmpeg

# Enforce FastSID for very weak CPUs
ifeq ($(BR2_mipsel)$(BR2_arm1176jzf_s)$(BR2_cortex_a7),y)
VICE_CONF_OPTS += --without-resid
endif

ifeq ($(BR2_PACKAGE_MPG123),y)
VICE_CONF_OPTS += --with-mpg123
VICE_DEPENDENCIES += mpg123
endif

ifeq ($(BR2_PACKAGE_FLAC),y)
VICE_CONF_OPTS += --with-flac
VICE_DEPENDENCIES += flac
endif

ifeq ($(BR2_PACKAGE_LAME),y)
VICE_CONF_OPTS += --with-lame
VICE_DEPENDENCIES += lame
endif

ifeq ($(BR2_PACKAGE_LIBPNG),y)
VICE_CONF_OPTS += --with-png
VICE_DEPENDENCIES += libpng
endif

ifeq ($(BR2_PACKAGE_ZLIB),y)
VICE_CONF_OPTS += --with-zlib
VICE_DEPENDENCIES += zlib
endif

ifeq ($(BR2_PACKAGE_LIBVORBIS),y)
VICE_CONF_OPTS += --with-vorbis
VICE_DEPENDENCIES += libvorbis
endif

VICE_CONF_ENV += LDFLAGS=-lSDL2

ifeq ($(BR2_PACKAGE_VICE_X64),y)
VICE_TARGETS += x64
endif
ifeq ($(BR2_PACKAGE_VICE_X64DTV),y)
VICE_TARGETS += x64dtv
endif
ifeq ($(BR2_PACKAGE_VICE_X64SC),y)
VICE_TARGETS += x64sc
endif
ifeq ($(BR2_PACKAGE_VICE_XSCPU64),y)
VICE_TARGETS += xscpu64
endif
ifeq ($(BR2_PACKAGE_VICE_X128),y)
VICE_TARGETS += x128
endif
ifeq ($(BR2_PACKAGE_VICE_XVIC),y)
VICE_TARGETS += xvic
endif
ifeq ($(BR2_PACKAGE_VICE_XPET),y)
VICE_TARGETS += xpet
endif
ifeq ($(BR2_PACKAGE_VICE_XPLUS4),y)
VICE_TARGETS += xplus4
endif
ifeq ($(BR2_PACKAGE_VICE_XCBM2),y)
VICE_TARGETS += xcbm2
endif

define VICE_BUILD_CMDS
	# Workaround for build failure on liblinenoise-ng
	cd $(@D)/src/lib/linenoise-ng && $(MAKE)
	# Build all targets, -j1 to workaround some build issues
	for target in $(VICE_TARGETS); do \
        	$(MAKE) -j1 -C $(@D) $$target CFLAGS="$(TARGET_CFLAGS) -flto=auto" LDFLAGS="$(TARGET_LDFLAGS) -flto=auto"; \
    	done
endef

define VICE_KEEP_ONLY_SELECTED_TARGETS
	rm -Rf $(TARGET_DIR)/usr/bin/vsid ;
	rm -Rf $(TARGET_DIR)/usr/bin/c1541 ;
endef
VICE_KEEP_ONLY_SELECTED_TARGETS += $(if $(BR2_PACKAGE_VICE_X64DTV),, rm -Rf $(TARGET_DIR)/usr/bin/x64dtv ; )
VICE_KEEP_ONLY_SELECTED_TARGETS += $(if $(BR2_PACKAGE_VICE_X64SC),, rm -Rf $(TARGET_DIR)/usr/bin/x64sc ; )
VICE_KEEP_ONLY_SELECTED_TARGETS += $(if $(BR2_PACKAGE_VICE_XSCPU64),, rm -Rf $(TARGET_DIR)/usr/bin/xscpu64 ; )

define VICE_POST_PROCESS_EVMAPY
	mkdir -p $(TARGET_DIR)/usr/share/evmapy
	cp -f $(BR2_EXTERNAL_REGLINUX_PATH)/package/emulators/vice/c64.vice.keys \
        $(TARGET_DIR)/usr/share/evmapy
	cp -f $(BR2_EXTERNAL_REGLINUX_PATH)/package/emulators/vice/c128.vice.keys \
        $(TARGET_DIR)/usr/share/evmapy
endef

VICE_POST_INSTALL_TARGET_HOOKS += VICE_POST_PROCESS_EVMAPY
VICE_POST_INSTALL_TARGET_HOOKS += VICE_KEEP_ONLY_SELECTED_TARGETS

$(eval $(autotools-package))
