################################################################################
#
# retroarch
#
################################################################################

RETROARCH_VERSION = v1.20.0
RETROARCH_SITE = $(call github,libretro,RetroArch,$(RETROARCH_VERSION))
RETROARCH_LICENSE = GPLv3+
RETROARCH_DEPENDENCIES = host-pkgconf dejavu retroarch-assets flac noto-cjk-fonts gamemode
RETROARCH_DEPENDENCIES += libusb hidapi
# install in staging for debugging (gdb)
RETROARCH_INSTALL_STAGING = YES

RETROARCH_CONF_OPTS = --disable-oss --enable-zlib --disable-qt --enable-threads \
		      --enable-ozone --enable-xmb --disable-discord --enable-flac \
		      --enable-lua --enable-networking --enable-translate --enable-rgui \
		      --disable-cdrom --disable-videocore --disable-x11 --enable-xdelta \
		      --enable-hid --enable-libusb

ifeq ($(BR2_ENABLE_DEBUG),y)
    RETROARCH_CONF_OPTS += --enable-debug
endif

ifeq ($(BR2_PACKAGE_FFMPEG),y)
    RETROARCH_CONF_OPTS += --enable-ffmpeg
    RETROARCH_DEPENDENCIES += ffmpeg
else
    RETROARCH_CONF_OPTS += --disable-ffmpeg
endif

ifeq ($(BR2_PACKAGE_SDL2),y)
    RETROARCH_CONF_OPTS += --enable-sdl2
    RETROARCH_DEPENDENCIES += sdl2
else
    RETROARCH_CONF_OPTS += --disable-sdl2
	ifeq ($(BR2_PACKAGE_SDL),y)
        RETROARCH_CONF_OPTS += --enable-sdl
        RETROARCH_DEPENDENCIES += sdl
	else
        RETROARCH_CONF_OPTS += --disable-sdl
	endif
endif

ifeq ($(BR2_PACKAGE_LIBDRM),y)
    RETROARCH_CONF_OPTS += --enable-kms
endif

ifeq ($(BR2_ARM_FPU_NEON_VFPV4)$(BR2_ARM_FPU_NEON)$(BR2_ARM_FPU_NEON_FP_ARMV8),y)
    RETROARCH_CONF_OPTS += --enable-neon
endif

ifeq ($(BR2_GCC_TARGET_FLOAT_ABI),hard)
    RETROARCH_CONF_OPTS += --enable-floathard
endif

ifeq ($(BR2_PACKAGE_ALSA_LIB),y)
    RETROARCH_CONF_OPTS += --enable-alsa
    RETROARCH_DEPENDENCIES += alsa-lib
else
    RETROARCH_CONF_OPTS += --disable-alsa
endif

ifeq ($(BR2_PACKAGE_PULSEAUDIO),y)
    RETROARCH_CONF_OPTS += --enable-pulse
    RETROARCH_DEPENDENCIES += pulseaudio
else
    RETROARCH_CONF_OPTS += --disable-pulse
endif

# REG: add pipewire
ifeq ($(BR2_PACKAGE_PIPEWIRE),y)
    RETROARCH_CONF_OPTS += --enable-pipewire
    RETROARCH_DEPENDENCIES += pipewire
else
    RETROARCH_CONF_OPTS += --disable-pipewire
endif

# REG: favor desktop GL, if not available, fallbacks to GLES3 then GLES2
ifeq ($(BR2_PACKAGE_HAS_LIBGL),y)
  RETROARCH_CONF_OPTS += --enable-opengl
  RETROARCH_DEPENDENCIES += libgl
else ifeq ($(BR2_PACKAGE_HAS_GLES3),y)
    RETROARCH_CONF_OPTS += --enable-opengles3 --enable-opengles --enable-opengles3_1
    RETROARCH_DEPENDENCIES += libgles
# Panfrost does NOT support OpenGL ES 3.2
ifeq ($(BR2_PACKAGE_SYSTEM_TARGET_SM8250)$(BR2_PACKAGE_SYSTEM_TARGET_SM8550)$(BR2_PACKAGE_SYSTEM_TARGET_ASAHI)$(BR2_x86_64),y)
    RETROARCH_CONF_OPTS += --enable-opengles3_2
endif
else ifeq ($(BR2_PACKAGE_HAS_GLES2),y)
    RETROARCH_CONF_OPTS += --enable-opengles
    RETROARCH_DEPENDENCIES += libgles
endif

ifeq ($(BR2_PACKAGE_HAS_LIBEGL),y)
    RETROARCH_CONF_OPTS += --enable-egl
    RETROARCH_DEPENDENCIES += libegl
else
    RETROARCH_CONF_OPTS += --disable-egl
endif

ifeq ($(BR2_PACKAGE_HAS_LIBOPENVG),y)
    RETROARCH_DEPENDENCIES += libopenvg
endif

ifeq ($(BR2_PACKAGE_ZLIB),y)
    RETROARCH_CONF_OPTS += --enable-zlib
    RETROARCH_DEPENDENCIES += zlib
else
    RETROARCH_CONF_OPTS += --disable-zlib
endif

ifeq ($(BR2_PACKAGE_UDEV),y)
    RETROARCH_DEPENDENCIES += udev
endif

ifeq ($(BR2_PACKAGE_FREETYPE),y)
    RETROARCH_CONF_OPTS += --enable-freetype
    RETROARCH_DEPENDENCIES += freetype
else
    RETROARCH_CONF_OPTS += --disable-freetype
endif

#REG: deprecate rga
#ifeq ($(BR2_PACKAGE_ROCKCHIP_RGA),y)
#    RETROARCH_DEPENDENCIES += rockchip-rga
#endif

#REG: enforce EGL_NO_X11 since we do not build RA with X11 support
#ifeq ($(BR2_PACKAGE_XSERVER_XORG_SERVER),)
#	ifeq ($(BR2_PACKAGE_MESA3D_OPENGL_EGL),y)
          RETROARCH_TARGET_CFLAGS += -DEGL_NO_X11
#	endif
#endif

ifeq ($(BR2_PACKAGE_WAYLAND)$(BR2_PACKAGE_SWAY),yy)
    RETROARCH_CONF_OPTS += --enable-wayland
else
    RETROARCH_CONF_OPTS += --disable-wayland
endif

ifeq ($(BR2_PACKAGE_REGLINUX_VULKAN),y)
    RETROARCH_CONF_OPTS += --enable-vulkan
    RETROARCH_DEPENDENCIES += vulkan-headers vulkan-loader slang-shaders
endif

ifeq ($(BR2_riscv),y)
	RETROARCH_TARGET_CFLAGS += -DMESA_EGL_NO_X11_HEADERS=1
endif

define RETROARCH_CONFIGURE_CMDS
	(cd $(@D); rm -rf config.cache; \
		$(TARGET_CONFIGURE_ARGS) \
		$(TARGET_CONFIGURE_OPTS) \
		CFLAGS="$(TARGET_CFLAGS) $(RETROARCH_TARGET_CFLAGS)" \
		LDFLAGS="$(TARGET_LDFLAGS) $(RETROARCH_TARGET_LDFLAGS) -lc" \
		CROSS_COMPILE="$(HOST_DIR)/usr/bin/" \
		./configure \
		--prefix=/usr \
		$(RETROARCH_CONF_OPTS) \
	)
endef

define RETROARCH_BUILD_CMDS
	$(TARGET_CONFIGURE_OPTS) $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" LD="$(TARGET_LD)" -C $(@D)/
	$(TARGET_CONFIGURE_OPTS) $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" LD="$(TARGET_LD)" -C $(@D)/gfx/video_filters
	$(TARGET_CONFIGURE_OPTS) $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" LD="$(TARGET_LD)" -C $(@D)/libretro-common/audio/dsp_filters
endef

define RETROARCH_INSTALL_TARGET_CMDS
	$(MAKE) CXX="$(TARGET_CXX)" -C $(@D) DESTDIR=$(TARGET_DIR) install

	mkdir -p $(TARGET_DIR)/usr/share/video_filters
	cp $(@D)/gfx/video_filters/*.so $(TARGET_DIR)/usr/share/video_filters
	cp $(@D)/gfx/video_filters/*.filt $(TARGET_DIR)/usr/share/video_filters

	mkdir -p $(TARGET_DIR)/usr/share/audio_filters
	cp $(@D)/libretro-common/audio/dsp_filters/*.so $(TARGET_DIR)/usr/share/audio_filters
	cp $(@D)/libretro-common/audio/dsp_filters/*.dsp $(TARGET_DIR)/usr/share/audio_filters
endef

define RETROARCH_INSTALL_STAGING_CMDS
	$(MAKE) CXX="$(TARGET_CXX)" -C $(@D) DESTDIR=$(STAGING_DIR) install
endef

$(eval $(generic-package))

# DEFINITION OF LIBRETRO PLATFORM
LIBRETRO_PLATFORM = unix

ifeq ($(BR2_arm),y)
    ifeq ($(BR2_cortex_a7),y)
        LIBRETRO_PLATFORM += armv7
    else ifeq ($(BR2_cortex_a9),y)
        LIBRETRO_PLATFORM += armv7
	else ifeq ($(BR2_cortex_a15),y)
        LIBRETRO_PLATFORM += armv7
	else ifeq ($(BR2_cortex_a17),y)
        LIBRETRO_PLATFORM += armv7
    else ifeq ($(BR2_cortex_a15_a7),y)
        LIBRETRO_PLATFORM += armv7
	endif
endif

ifeq ($(BR2_aarch64),y)
    LIBRETRO_PLATFORM += arm64
endif

ifeq ($(BR2_ARM_CPU_HAS_NEON),y)
    LIBRETRO_PLATFORM += neon
endif

ifeq ($(BR2_PACKAGE_SYSTEM_TARGET_BCM2835),y)
    LIBRETRO_PLATFORM += rpi armv
endif

ifeq ($(BR2_PACKAGE_SYSTEM_TARGET_BCM2836),y)
    LIBRETRO_PLATFORM += rpi2
endif

ifeq ($(BR2_PACKAGE_SYSTEM_TARGET_BCM2837),y)
    LIBRETRO_PLATFORM += rpi3_64
endif

ifeq ($(BR2_PACKAGE_SYSTEM_TARGET_BCM2711),y)
    LIBRETRO_PLATFORM += rpi4_64
endif

ifeq ($(BR2_PACKAGE_SYSTEM_TARGET_BCM2712),y)
    LIBRETRO_PLATFORM += rpi5_64
endif
