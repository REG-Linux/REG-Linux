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

ifeq ($(BR2_arm1176jzf_s),y)
DOSBOX_STAGING_CFLAGS   += -mcpu=arm1176jzf-s -mfpu=vfp -mfloat-abi=hard
DOSBOX_STAGING_CXXFLAGS += -mcpu=arm1176jzf-s -mfpu=vfp -mfloat-abi=hard
endif

ifeq ($(BR2_cortex_a7),y)
DOSBOX_STAGING_CFLAGS   += -marm -march=armv7-a -mfpu=neon-vfpv4 -mfloat-abi=hard
DOSBOX_STAGING_CXXFLAGS += -marm -march=armv7-a -mfpu=neon-vfpv4 -mfloat-abi=hard
endif

ifeq ($(BR2_cortex_a9),y)
DOSBOX_STAGING_CFLAGS   += -marm -march=armv7-a -mtune=cortex-a9 -mfpu=neon-vfpv3 -mfloat-abi=hard
DOSBOX_STAGING_CXXFLAGS += -marm -march=armv7-a -mtune=cortex-a9 -mfpu=neon-vfpv3 -mfloat-abi=hard
endif

ifeq ($(BR2_cortex_a15_a7),y)
DOSBOX_STAGING_CFLAGS   += -marm -march=armv7-a -mcpu=cortex-a15.cortex-a7 -mtune=cortex-a15.cortex-a7 -mfpu=neon-vfpv4 -mfloat-abi=hard
DOSBOX_STAGING_CXXFLAGS += -marm -march=armv7-a -mcpu=cortex-a15.cortex-a7 -mtune=cortex-a15.cortex-a7 -mfpu=neon-vfpv4 -mfloat-abi=hard
endif

ifeq ($(BR2_cortex_a17),y)
DOSBOX_STAGING_CFLAGS   += -marm -march=armv7-a -mcpu=cortex-a17 -mtune=cortex-a17 -mfpu=neon-vfpv4 -mfloat-abi=hard
DOSBOX_STAGING_CXXFLAGS += -marm -march=armv7-a -mcpu=cortex-a17 -mtune=cortex-a17 -mfpu=neon-vfpv4 -mfloat-abi=hard
endif

ifeq ($(BR2_cortex_a35),y)
DOSBOX_STAGING_CFLAGS   += -march=armv8-a+crc -mcpu=cortex-a35 -mtune=cortex-a35
DOSBOX_STAGING_CXXFLAGS += -march=armv8-a+crc -mcpu=cortex-a35 -mtune=cortex-a35
endif

ifeq ($(BR2_cortex_a53),y)
DOSBOX_STAGING_CFLAGS   += -march=armv8-a+crc -mcpu=cortex-a53 -mtune=cortex-a53
DOSBOX_STAGING_CXXFLAGS += -march=armv8-a+crc -mcpu=cortex-a53 -mtune=cortex-a53
endif

ifeq ($(BR2_cortex_a72),y)
DOSBOX_STAGING_CFLAGS   += -march=armv8-a+crc -mcpu=cortex-a72 -mtune=cortex-a72
DOSBOX_STAGING_CXXFLAGS += -march=armv8-a+crc -mcpu=cortex-a72 -mtune=cortex-a72
endif

ifeq ($(BR2_cortex_a73_a53),y)
DOSBOX_STAGING_CFLAGS   += -march=armv8-a+crc -mcpu=cortex-a73.cortex-a53 -mtune=cortex-a73.cortex-a53
DOSBOX_STAGING_CXXFLAGS += -march=armv8-a+crc -mcpu=cortex-a73.cortex-a53 -mtune=cortex-a73.cortex-a53
endif

ifeq ($(BR2_cortex_a55),y)
DOSBOX_STAGING_CFLAGS   += -march=armv8.2-a+crc+crypto -mcpu=cortex-a55 -mtune=cortex-a55
DOSBOX_STAGING_CXXFLAGS += -march=armv8.2-a+crc+crypto -mcpu=cortex-a55 -mtune=cortex-a55
endif

ifeq ($(BR2_cortex_a75_a55),y)
DOSBOX_STAGING_CFLAGS   += -march=armv8.2-a+crc -mcpu=cortex-a75.cortex-a55 -mtune=cortex-a75.cortex-a55
DOSBOX_STAGING_CXXFLAGS += -march=armv8.2-a+crc -mcpu=cortex-a75.cortex-a55 -mtune=cortex-a75.cortex-a55
endif

ifeq ($(BR2_cortex_a76_a55),y)
DOSBOX_STAGING_CFLAGS   += -march=armv8.2-a+dotprod+rcpc+ssbs+sb -mcpu=cortex-a76.cortex-a55 -mtune=cortex-a76.cortex-a55
DOSBOX_STAGING_CXXFLAGS += -march=armv8.2-a+dotprod+rcpc+ssbs+sb -mcpu=cortex-a76.cortex-a55 -mtune=cortex-a76.cortex-a55
endif

define DOSBOX_STAGING_INSTALL_TARGET_CMDS
        $(INSTALL) -D $(@D)/build/dosbox $(TARGET_DIR)/usr/bin/dosbox-staging
endef

$(eval $(meson-package))
