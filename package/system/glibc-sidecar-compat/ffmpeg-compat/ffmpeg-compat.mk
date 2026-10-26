################################################################################
#
# ffmpeg-compat
#
# FFmpeg 4.4 for the glibc sidecar: libavcodec.so.58, libavformat.so.58,
# libavutil.so.56, libswscale.so.5 and libswresample.so.3, which ports built
# on Ubuntu 20.04/22.04 link. Libraries only, with FFmpeg's own decoders and
# zlib; no headers, nothing in the sidecar builds against them. Cross
# options as buildroot's ffmpeg.
#
################################################################################

FFMPEG_COMPAT_VERSION = 4.4.6
FFMPEG_COMPAT_SITE = https://ffmpeg.org/releases
FFMPEG_COMPAT_SOURCE = ffmpeg-$(FFMPEG_COMPAT_VERSION).tar.xz
FFMPEG_COMPAT_DL_SUBDIR = ffmpeg
FFMPEG_COMPAT_LICENSE = LGPL-2.1+
FFMPEG_COMPAT_LICENSE_FILES = LICENSE.md COPYING.LGPLv2.1
FFMPEG_COMPAT_DEPENDENCIES = host-pkgconf zlib bzip2

# No LTO: FFmpeg 4's inline assembly doesn't survive it
FFMPEG_COMPAT_CFLAGS = $(filter-out -flto%,$(TARGET_CFLAGS))
ifeq ($(BR2_ARM_INSTRUCTIONS_THUMB),y)
FFMPEG_COMPAT_CFLAGS += -marm
endif
FFMPEG_COMPAT_LDFLAGS = $(filter-out -flto%,$(TARGET_LDFLAGS))

FFMPEG_COMPAT_CONF_OPTS = \
	--prefix=/usr \
	--enable-shared \
	--disable-static \
	--disable-programs \
	--disable-doc \
	--disable-avdevice \
	--disable-avfilter \
	--disable-postproc \
	--disable-debug \
	--disable-lto \
	--enable-pic \
	--enable-runtime-cpudetect \
	--enable-zlib \
	--enable-bzlib \
	--disable-iconv \
	--disable-vaapi \
	--disable-vdpau \
	--disable-xlib \
	--disable-libxcb \
	--disable-sdl2 \
	--disable-alsa \
	--disable-sndio \
	--disable-v4l2-m2m

ifeq ($(BR2_aarch64),y)
FFMPEG_COMPAT_CONF_OPTS += --enable-neon
else ifeq ($(BR2_arm),y)
FFMPEG_COMPAT_CONF_OPTS += --enable-armv6 --enable-vfp
FFMPEG_COMPAT_CONF_OPTS += $(if $(BR2_ARM_CPU_HAS_NEON),--enable-neon,--disable-neon)
endif

ifneq ($(GCC_TARGET_CPU),)
FFMPEG_COMPAT_CONF_OPTS += --cpu="$(GCC_TARGET_CPU)"
else ifneq ($(GCC_TARGET_ARCH),)
FFMPEG_COMPAT_CONF_OPTS += --cpu="$(GCC_TARGET_ARCH)"
endif

define FFMPEG_COMPAT_CONFIGURE_CMDS
	(cd $(@D) && rm -rf config.cache && \
	$(TARGET_CONFIGURE_OPTS) \
	$(TARGET_CONFIGURE_ARGS) \
	CFLAGS="$(FFMPEG_COMPAT_CFLAGS)" \
	LDFLAGS="$(FFMPEG_COMPAT_LDFLAGS)" \
	./configure \
		--enable-cross-compile \
		--cross-prefix=$(TARGET_CROSS) \
		--sysroot=$(STAGING_DIR) \
		--host-cc="$(HOSTCC)" \
		--arch=$(BR2_ARCH) \
		--target-os="linux" \
		--disable-stripping \
		--pkg-config="$(PKG_CONFIG_HOST_BINARY)" \
		$(FFMPEG_COMPAT_CONF_OPTS) \
	)
endef

define FFMPEG_COMPAT_BUILD_CMDS
	$(TARGET_MAKE_ENV) $(MAKE) -C $(@D)
endef

define FFMPEG_COMPAT_INSTALL_TARGET_CMDS
	for l in avcodec.so.58 avformat.so.58 avutil.so.56 swscale.so.5 swresample.so.3; do \
		cp -a $(@D)/lib$${l%%.so.*}/lib$$l* $(TARGET_DIR)/usr/lib/ || exit 1; \
	done
endef

$(eval $(generic-package))
