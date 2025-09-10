################################################################################
#
# dosbox-staging
#
################################################################################

# Release 0.82.2 on Apr 27, 2025
DOSBOX_STAGING_VERSION = v0.82.2
DOSBOX_STAGING_SITE = $(call github,dosbox-staging,dosbox-staging,$(DOSBOX_STAGING_VERSION))
DOSBOX_STAGING_DEPENDENCIES = alsa-lib sdl2 sdl2_net sdl2_image zlib libpng libogg libvorbis opus opusfile slirp iir speexdsp
DOSBOX_STAGING_LICENSE = GPLv2

DOSBOX_STAGING_CPPFLAGS = -DNDEBUG
DOSBOX_STAGING_CFLAGS   = -O3 -fstrict-aliasing -fno-signed-zeros -fno-trapping-math -fassociative-math -frename-registers -ffunction-sections -fdata-sections
DOSBOX_STAGING_CXXFLAGS = -O3 -fstrict-aliasing -fno-signed-zeros -fno-trapping-math -fassociative-math -frename-registers -ffunction-sections -fdata-sections

# Fluidsynth for MIDI emulation
ifeq ($(BR2_PACKAGE_FLUIDSYNTH),y)
DOSBOX_STAGING_DEPENDENCIES += fluidsynth
DOSBOX_STAGING_CONF_OPTS += -Duse_fluidsynth=true
else
DOSBOX_STAGING_CONF_OPTS += -Duse_fluidsynth=false
endif

# Roland MT-32 emulation
ifeq ($(BR2_PACKAGE_LIBMT32EMU),y)
DOSBOX_STAGING_DEPENDENCIES += libmt32emu
DOSBOX_STAGING_CONF_OPTS += -Duse_mt32emu=true
else
DOSBOX_STAGING_CONF_OPTS += -Duse_mt32emu=false
endif

# OpenGL support (no GLES support yet)
ifeq ($(BR2_PACKAGE_HAS_LIBGL),y)
DOSBOX_STAGING_DEPENDENCIES += libgl
DOSBOX_STAGING_CONF_OPTS += -Duse_opengl=true
else
DOSBOX_STAGING_CONF_OPTS += -Duse_opengl=false
endif

define DOSBOX_STAGING_INSTALL_TARGET_CMDS
        $(INSTALL) -D $(@D)/buildroot-build/dosbox $(TARGET_DIR)/usr/bin/dosbox-staging
endef

$(eval $(meson-package))
