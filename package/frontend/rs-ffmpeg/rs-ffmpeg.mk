################################################################################
#
# rs-ffmpeg
#
################################################################################

RS_FFMPEG_VERSION = 7.1.2
RS_FFMPEG_SOURCE = ffmpeg-$(RS_FFMPEG_VERSION).tar.xz
RS_FFMPEG_SITE = https://ffmpeg.org/releases
RS_FFMPEG_INSTALL_STAGING = YES

RS_FFMPEG_LICENSE = LGPL-2.1+, libjpeg license
RS_FFMPEG_LICENSE_FILES = LICENSE.md COPYING.LGPLv2.1

RS_FFMPEG_CPE_ID_VENDOR = ffmpeg

RS_FFMPEG_CONF_OPTS = \
	--prefix=/usr \
	--enable-avfilter \
	--disable-version3 \
	--enable-logging \
	--enable-optimizations \
	--disable-extra-warnings \
	--enable-avdevice \
	--enable-avcodec \
	--enable-avformat \
	--disable-protocols \
	--enable-protocol=file \
	--disable-network \
	--disable-gray \
	--enable-swscale-alpha \
	--disable-small \
	--disable-dxva2 \
	--enable-runtime-cpudetect \
	--disable-hardcoded-tables \
	--disable-mipsdsp \
	--disable-mipsdspr2 \
	--disable-msa \
	--enable-hwaccels \
	--disable-cuda \
	--disable-cuvid \
	--disable-nvenc \
	--disable-avisynth \
	--disable-frei0r \
	--disable-libopencore-amrnb \
	--disable-libopencore-amrwb \
	--disable-libdc1394 \
	--disable-libgsm \
	--disable-libilbc \
	--disable-libvo-amrwbenc \
	--disable-symver \
	--disable-doc \

RS_FFMPEG_LOCAL_ONLY_DECODERS = h264 hevc vp9 vp8 av1 mpeg4 mpeg2video aac mp3 opus vorbis flac pcm_s16le pcm_u8 mjpeg
# V4L2 mem2mem wrappers for VideoHardwareDecoding in REG-Station
RS_FFMPEG_LOCAL_ONLY_DECODERS += h264_v4l2m2m hevc_v4l2m2m vp8_v4l2m2m vp9_v4l2m2m mpeg4_v4l2m2m mpeg2_v4l2m2m
RS_FFMPEG_LOCAL_ONLY_DEMUXERS = mov matroska avi ogg wav flac mp3
RS_FFMPEG_LOCAL_ONLY_PARSERS = h264 hevc vp9 vp8 av1 mpeg4video aac mpegaudio opus vorbis flac
RS_FFMPEG_LOCAL_ONLY_PROTOCOLS = file
RS_FFMPEG_LOCAL_ONLY_FILTERS = format aresample aformat asetnsamples

RS_FFMPEG_CONF_OPTS += --libdir=/usr/lib/rs-ffmpeg

RS_FFMPEG_DEPENDENCIES += host-pkgconf

RS_FFMPEG_CONF_OPTS += --disable-gpl
RS_FFMPEG_CONF_OPTS += --disable-nonfree
RS_FFMPEG_CONF_OPTS += --disable-ffmpeg
RS_FFMPEG_CONF_OPTS += --disable-ffplay
RS_FFMPEG_CONF_OPTS += --disable-libjack
RS_FFMPEG_CONF_OPTS += --disable-libpulse
RS_FFMPEG_CONF_OPTS += --disable-ffprobe
RS_FFMPEG_CONF_OPTS += --disable-libxcb
RS_FFMPEG_CONF_OPTS += --disable-postproc
RS_FFMPEG_CONF_OPTS += --disable-encoders
RS_FFMPEG_CONF_OPTS += --disable-muxers
RS_FFMPEG_CONF_OPTS += --disable-libfdk-aac
RS_FFMPEG_CONF_OPTS += --disable-gnutls
RS_FFMPEG_CONF_OPTS += --disable-openssl
RS_FFMPEG_CONF_OPTS += --disable-libopencv

ifeq ($(BR2_PACKAGE_LIBV4L),y)
RS_FFMPEG_DEPENDENCIES += libv4l
RS_FFMPEG_CONF_OPTS += --enable-libv4l2
else
RS_FFMPEG_CONF_OPTS += --disable-libv4l2
endif

ifeq ($(BR2_PACKAGE_RS_FFMPEG_SWSCALE),y)
RS_FFMPEG_CONF_OPTS += --enable-swscale
else
RS_FFMPEG_CONF_OPTS += --disable-swscale
endif

ifneq ($(call qstrip,$(BR2_PACKAGE_RS_FFMPEG_DECODERS)),all)
RS_FFMPEG_CONF_OPTS += --disable-decoders \
	$(foreach x,$(call qstrip,$(BR2_PACKAGE_RS_FFMPEG_DECODERS)),--enable-decoder=$(x))
endif

ifneq ($(call qstrip,$(BR2_PACKAGE_RS_FFMPEG_DEMUXERS)),all)
RS_FFMPEG_CONF_OPTS += --disable-demuxers \
	$(foreach x,$(call qstrip,$(BR2_PACKAGE_RS_FFMPEG_DEMUXERS)),--enable-demuxer=$(x))
endif

ifneq ($(call qstrip,$(BR2_PACKAGE_RS_FFMPEG_PARSERS)),all)
RS_FFMPEG_CONF_OPTS += --disable-parsers \
	$(foreach x,$(call qstrip,$(BR2_PACKAGE_RS_FFMPEG_PARSERS)),--enable-parser=$(x))
endif

ifneq ($(call qstrip,$(BR2_PACKAGE_RS_FFMPEG_BSFS)),all)
RS_FFMPEG_CONF_OPTS += --disable-bsfs \
	$(foreach x,$(call qstrip,$(BR2_PACKAGE_RS_FFMPEG_BSFS)),--enable-bsf=$(x))
endif


ifneq ($(call qstrip,$(BR2_PACKAGE_RS_FFMPEG_FILTERS)),all)
RS_FFMPEG_CONF_OPTS += --disable-filters \
	$(foreach x,$(call qstrip,$(BR2_PACKAGE_RS_FFMPEG_FILTERS)),--enable-filter=$(x))
endif

ifeq ($(BR2_PACKAGE_RS_FFMPEG_INDEVS),y)
RS_FFMPEG_CONF_OPTS += --enable-indevs
RS_FFMPEG_CONF_OPTS += --disable-alsa
else
RS_FFMPEG_CONF_OPTS += --disable-indevs
endif

ifeq ($(BR2_PACKAGE_RS_FFMPEG_OUTDEVS),y)
RS_FFMPEG_CONF_OPTS += --enable-outdevs
ifeq ($(BR2_PACKAGE_ALSA_LIB),y)
RS_FFMPEG_DEPENDENCIES += alsa-lib
endif
else
RS_FFMPEG_CONF_OPTS += --disable-outdevs
endif

ifeq ($(BR2_TOOLCHAIN_HAS_THREADS),y)
RS_FFMPEG_CONF_OPTS += --enable-pthreads
else
RS_FFMPEG_CONF_OPTS += --disable-pthreads
endif

ifeq ($(BR2_PACKAGE_ZLIB),y)
RS_FFMPEG_CONF_OPTS += --enable-zlib
RS_FFMPEG_DEPENDENCIES += zlib
else
RS_FFMPEG_CONF_OPTS += --disable-zlib
endif

ifeq ($(BR2_PACKAGE_BZIP2),y)
RS_FFMPEG_CONF_OPTS += --enable-bzlib
RS_FFMPEG_DEPENDENCIES += bzip2
else
RS_FFMPEG_CONF_OPTS += --disable-bzlib
endif


RS_FFMPEG_CONF_OPTS += --disable-libcdio

ifeq ($(BR2_PACKAGE_LIBDRM),y)
RS_FFMPEG_CONF_OPTS += --enable-libdrm
RS_FFMPEG_DEPENDENCIES += libdrm
else
RS_FFMPEG_CONF_OPTS += --disable-libdrm
endif

RS_FFMPEG_CONF_OPTS += --disable-libopenh264
RS_FFMPEG_CONF_OPTS += --disable-libvorbis

# REG - v4l2-request requires kernel headers >= 4.20 (v4l2_timeval_to_ns, media request API)
ifeq ($(BR2_PACKAGE_LIBDRM)$(BR2_PACKAGE_LIBV4L)$(BR2_TOOLCHAIN_HEADERS_AT_LEAST_4_20),yyy)
RS_FFMPEG_CONF_OPTS += --enable-v4l2-request
RS_FFMPEG_DEPENDENCIES += libv4l
else
RS_FFMPEG_CONF_OPTS += --disable-v4l2-request
endif

ifeq ($(BR2_PACKAGE_LIBVA),y)
RS_FFMPEG_CONF_OPTS += --enable-vaapi
RS_FFMPEG_DEPENDENCIES += libva
else
RS_FFMPEG_CONF_OPTS += --disable-vaapi
endif

ifeq ($(BR2_PACKAGE_LIBVDPAU),y)
RS_FFMPEG_CONF_OPTS += --enable-vdpau
RS_FFMPEG_DEPENDENCIES += libvdpau
else
RS_FFMPEG_CONF_OPTS += --disable-vdpau
endif

ifeq ($(BR2_PACKAGE_RPI_USERLAND),y)
RS_FFMPEG_CONF_OPTS += --enable-omx --enable-omx-rpi \
	--extra-cflags=-I$(STAGING_DIR)/usr/include/IL
RS_FFMPEG_DEPENDENCIES += rpi-userland
ifeq ($(BR2_arm),y)
RS_FFMPEG_CONF_OPTS += --enable-mmal
else
RS_FFMPEG_CONF_OPTS += --disable-mmal
endif
else
RS_FFMPEG_CONF_OPTS += --disable-mmal --disable-omx --disable-omx-rpi
endif

ifeq ($(BR2_PACKAGE_OPUS),y)
RS_FFMPEG_CONF_OPTS += --enable-libopus
RS_FFMPEG_DEPENDENCIES += opus
else
RS_FFMPEG_CONF_OPTS += --disable-libopus
endif

ifeq ($(BR2_PACKAGE_LIBVPX),y)
RS_FFMPEG_CONF_OPTS += --enable-libvpx
RS_FFMPEG_DEPENDENCIES += libvpx
else
RS_FFMPEG_CONF_OPTS += --disable-libvpx
endif

RS_FFMPEG_CONF_OPTS += --disable-libass
RS_FFMPEG_CONF_OPTS += --disable-libbluray

ifeq ($(BR2_PACKAGE_LIBVPL),y)
RS_FFMPEG_CONF_OPTS += --enable-libvpl --disable-libmfx
RS_FFMPEG_DEPENDENCIES += libvpl
else ifeq ($(BR2_PACKAGE_INTEL_MEDIASDK),y)
RS_FFMPEG_CONF_OPTS += --disable-libvpl --enable-libmfx
RS_FFMPEG_DEPENDENCIES += intel-mediasdk
else
RS_FFMPEG_CONF_OPTS += --disable-libvpl --disable-libmfx
endif

RS_FFMPEG_CONF_OPTS += --disable-librtmp

RS_FFMPEG_CONF_OPTS += --disable-libmp3lame
RS_FFMPEG_CONF_OPTS += --disable-libmodplug
RS_FFMPEG_CONF_OPTS += --disable-libopenmpt
RS_FFMPEG_CONF_OPTS += --disable-libsoxr
RS_FFMPEG_CONF_OPTS += --disable-libspeex
RS_FFMPEG_CONF_OPTS += --disable-libtheora
RS_FFMPEG_CONF_OPTS += --disable-iconv
RS_FFMPEG_CONF_OPTS += --disable-libxml2
RS_FFMPEG_CONF_OPTS += --disable-libfreetype
RS_FFMPEG_CONF_OPTS += --disable-fontconfig
RS_FFMPEG_CONF_OPTS += --disable-libharfbuzz
RS_FFMPEG_CONF_OPTS += --disable-libfribidi
RS_FFMPEG_CONF_OPTS += --disable-libopenjpeg

RS_FFMPEG_CONF_OPTS += --disable-libx264
RS_FFMPEG_CONF_OPTS += --disable-libx265

ifeq ($(BR2_PACKAGE_DAV1D),y)
RS_FFMPEG_CONF_OPTS += --enable-libdav1d
RS_FFMPEG_DEPENDENCIES += dav1d
else
RS_FFMPEG_CONF_OPTS += --disable-libdav1d
endif

ifeq ($(BR2_X86_CPU_HAS_MMX),y)
RS_FFMPEG_CONF_OPTS += --enable-x86asm
RS_FFMPEG_DEPENDENCIES += host-nasm
else
RS_FFMPEG_CONF_OPTS += --disable-x86asm
RS_FFMPEG_CONF_OPTS += --disable-mmx
endif

ifeq ($(BR2_X86_CPU_HAS_SSE),y)
RS_FFMPEG_CONF_OPTS += --enable-sse
else
RS_FFMPEG_CONF_OPTS += --disable-sse
endif

ifeq ($(BR2_X86_CPU_HAS_SSE2),y)
RS_FFMPEG_CONF_OPTS += --enable-sse2
else
RS_FFMPEG_CONF_OPTS += --disable-sse2
endif

ifeq ($(BR2_X86_CPU_HAS_SSE3),y)
RS_FFMPEG_CONF_OPTS += --enable-sse3
else
RS_FFMPEG_CONF_OPTS += --disable-sse3
endif

ifeq ($(BR2_X86_CPU_HAS_SSSE3),y)
RS_FFMPEG_CONF_OPTS += --enable-ssse3
else
RS_FFMPEG_CONF_OPTS += --disable-ssse3
endif

ifeq ($(BR2_X86_CPU_HAS_SSE4),y)
RS_FFMPEG_CONF_OPTS += --enable-sse4
else
RS_FFMPEG_CONF_OPTS += --disable-sse4
endif

ifeq ($(BR2_X86_CPU_HAS_SSE42),y)
RS_FFMPEG_CONF_OPTS += --enable-sse42
else
RS_FFMPEG_CONF_OPTS += --disable-sse42
endif

ifeq ($(BR2_PACKAGE_RS_FFMPEG_LOCAL_ONLY),y)
RS_FFMPEG_CONF_OPTS += --disable-avdevice
#RS_FFMPEG_CONF_OPTS += --disable-avfilter
RS_FFMPEG_CONF_OPTS += --disable-indevs
RS_FFMPEG_CONF_OPTS += --disable-outdevs
RS_FFMPEG_CONF_OPTS += --disable-bsfs
RS_FFMPEG_CONF_OPTS += --disable-filters \
	$(foreach x,$(call qstrip,$(RS_FFMPEG_LOCAL_ONLY_FILTERS)),--enable-filter=$(x))
RS_FFMPEG_CONF_OPTS += --disable-decoders \
	$(foreach x,$(call qstrip,$(RS_FFMPEG_LOCAL_ONLY_DECODERS)),--enable-decoder=$(x))
RS_FFMPEG_CONF_OPTS += --disable-demuxers \
	$(foreach x,$(call qstrip,$(RS_FFMPEG_LOCAL_ONLY_DEMUXERS)),--enable-demuxer=$(x))
RS_FFMPEG_CONF_OPTS += --disable-parsers \
	$(foreach x,$(call qstrip,$(RS_FFMPEG_LOCAL_ONLY_PARSERS)),--enable-parser=$(x))
RS_FFMPEG_CONF_OPTS += --disable-protocols \
	$(foreach x,$(call qstrip,$(RS_FFMPEG_LOCAL_ONLY_PROTOCOLS)),--enable-protocol=$(x))
endif

ifeq ($(BR2_X86_CPU_HAS_AVX),y)
RS_FFMPEG_CONF_OPTS += --enable-avx
else
RS_FFMPEG_CONF_OPTS += --disable-avx
endif

ifeq ($(BR2_X86_CPU_HAS_AVX2),y)
RS_FFMPEG_CONF_OPTS += --enable-avx2
else
RS_FFMPEG_CONF_OPTS += --disable-avx2
endif

# Explicitly disable everything that doesn't match for ARM
# FFMPEG "autodetects" by compiling an extended instruction via AS
# This works on compilers that aren't built for generic by default
ifeq ($(BR2_ARM_CPU_ARMV4),y)
RS_FFMPEG_CONF_OPTS += --disable-armv5te
endif
ifeq ($(BR2_ARM_CPU_ARMV6)$(BR2_ARM_CPU_ARMV7A),y)
RS_FFMPEG_CONF_OPTS += --enable-armv6
else
RS_FFMPEG_CONF_OPTS += --disable-armv6 --disable-armv6t2
endif
ifeq ($(BR2_ARM_CPU_HAS_VFPV2),y)
RS_FFMPEG_CONF_OPTS += --enable-vfp
else
RS_FFMPEG_CONF_OPTS += --disable-vfp
endif
ifeq ($(BR2_ARM_CPU_HAS_NEON),y)
RS_FFMPEG_CONF_OPTS += --enable-neon
else ifeq ($(BR2_aarch64),y)
RS_FFMPEG_CONF_OPTS += --enable-neon
else
RS_FFMPEG_CONF_OPTS += --disable-neon
endif

ifeq ($(BR2_mips)$(BR2_mipsel)$(BR2_mips64)$(BR2_mips64el),y)
ifeq ($(BR2_MIPS_SOFT_FLOAT),y)
RS_FFMPEG_CONF_OPTS += --disable-mipsfpu
else
RS_FFMPEG_CONF_OPTS += --enable-mipsfpu
endif

# Fix build failure on several missing assembly instructions
RS_FFMPEG_CONF_OPTS += --disable-asm
endif # MIPS

ifeq ($(BR2_POWERPC_CPU_HAS_ALTIVEC):$(BR2_powerpc64le),y:)
RS_FFMPEG_CONF_OPTS += --enable-altivec
else ifeq ($(BR2_POWERPC_CPU_HAS_VSX):$(BR2_powerpc64le),y:y)
# On LE, ffmpeg AltiVec support needs VSX intrinsics, and VSX
# is an extension to AltiVec.
RS_FFMPEG_CONF_OPTS += --enable-altivec
else
RS_FFMPEG_CONF_OPTS += --disable-altivec
endif

# Fix build failure on several missing assembly instructions
ifeq ($(BR2_RISCV_32),y)
RS_FFMPEG_CONF_OPTS += --disable-rvv --disable-asm
endif

# Uses __atomic_fetch_add_4
ifeq ($(BR2_TOOLCHAIN_HAS_LIBATOMIC),y)
RS_FFMPEG_CONF_OPTS += --extra-libs=-latomic
endif

ifeq ($(BR2_STATIC_LIBS),)
RS_FFMPEG_CONF_OPTS += --enable-pic
else
RS_FFMPEG_CONF_OPTS += --disable-pic
endif

# Default to --cpu=generic for MIPS architecture, in order to avoid a
# warning from ffmpeg's configure script.
ifeq ($(BR2_mips)$(BR2_mipsel)$(BR2_mips64)$(BR2_mips64el),y)
RS_FFMPEG_CONF_OPTS += --cpu=generic
else ifneq ($(GCC_TARGET_CPU),)
RS_FFMPEG_CONF_OPTS += --cpu="$(GCC_TARGET_CPU)"
else ifneq ($(GCC_TARGET_ARCH),)
RS_FFMPEG_CONF_OPTS += --cpu="$(GCC_TARGET_ARCH)"
endif

RS_FFMPEG_CFLAGS = $(TARGET_CFLAGS)

ifeq ($(BR2_TOOLCHAIN_HAS_GCC_BUG_85180),y)
RS_FFMPEG_CONF_OPTS += --disable-optimizations
RS_FFMPEG_CFLAGS += -O0
endif

ifeq ($(BR2_TOOLCHAIN_HAS_GCC_BUG_68485),y)
RS_FFMPEG_CONF_OPTS += --disable-optimizations
RS_FFMPEG_CFLAGS += -O0
endif

ifeq ($(BR2_ARM_INSTRUCTIONS_THUMB),y)
RS_FFMPEG_CFLAGS += -marm
endif

RS_FFMPEG_CONF_ENV += CFLAGS="$(RS_FFMPEG_CFLAGS)"
RS_FFMPEG_CONF_OPTS += $(call qstrip,$(BR2_PACKAGE_RS_FFMPEG_EXTRACONF))

# Override RS_FFMPEG_CONFIGURE_CMDS: FFmpeg does not support --target and others
define RS_FFMPEG_CONFIGURE_CMDS
	(cd $(RS_FFMPEG_SRCDIR) && rm -rf config.cache && \
	$(TARGET_CONFIGURE_OPTS) \
	$(TARGET_CONFIGURE_ARGS) \
	$(RS_FFMPEG_CONF_ENV) \
	./configure \
		--enable-cross-compile \
		--cross-prefix=$(TARGET_CROSS) \
		--sysroot=$(STAGING_DIR) \
		--host-cc="$(HOSTCC)" \
		--arch=$(BR2_ARCH) \
		--target-os="linux" \
		--disable-stripping \
		--pkg-config="$(PKG_CONFIG_HOST_BINARY)" \
		$(SHARED_STATIC_LIBS_OPTS) \
		$(RS_FFMPEG_CONF_OPTS) \
	)
endef

define RS_FFMPEG_REMOVE_EXAMPLE_SRC_FILES
	rm -rf $(TARGET_DIR)/usr/share/ffmpeg/examples
endef
RS_FFMPEG_POST_INSTALL_TARGET_HOOKS += RS_FFMPEG_REMOVE_EXAMPLE_SRC_FILES

$(eval $(autotools-package))
