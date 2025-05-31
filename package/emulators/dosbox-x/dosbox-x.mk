################################################################################
#
# dosbox-x
#
################################################################################

DOSBOX_X_VERSION = dosbox-x-v2025.05.03
DOSBOX_X_SITE = $(call github,joncampbell123,dosbox-x,$(DOSBOX_X_VERSION))
DOSBOX_X_DEPENDENCIES = sdl2 sdl2_net zlib libpng libogg libvorbis linux-headers
DOSBOX_X_LICENSE = GPLv2

ifeq ($(BR2_PACKAGE_FLUIDSYNTH),y)
DOSBOX_X_DEPENDENCIES += fluidsynth
DOSBOX_X_FLUIDSYNTH_OPTS = --enable-fluidsynth
else
DOSBOX_X_FLUIDSYNTH_OPTS = --disable-fluidsynth
endif

define DOSBOX_X_CONFIGURE_CMDS
    cd $(@D); ./autogen.sh; \
        $(TARGET_CONFIGURE_OPTS) CROSS_COMPILE="$(HOST_DIR)/usr/bin/" \
        LIBS="-lvorbisfile -lvorbis -logg" \
        ./configure --host="$(GNU_TARGET_NAME)" \
                    --enable-core-inline \
                    --enable-dynrec \
                    --enable-unaligned_memory \
                    --prefix=/usr \
                    --disable-sdl \
                    --enable-sdl2 \
		    $(DOSBOX_X_FLUIDSYNTH_OPTS) \
                    --with-sdl2-prefix="$(STAGING_DIR)/usr";
endef

define DOSBOX_X_CONFIGURE_CONFIG
    mkdir -p $(TARGET_DIR)/usr/share/reglinux/datainit/system/configs/dosbox
    cp -rf $(@D)/dosbox-x.reference.conf \
        $(TARGET_DIR)/usr/share/reglinux/datainit/system/configs/dosbox/dosboxx.conf
endef

DOSBOX_X_POST_INSTALL_TARGET_HOOKS += DOSBOX_X_CONFIGURE_CONFIG

$(eval $(autotools-package))
