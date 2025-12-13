################################################################################
#
# es-ffmpeg
#
################################################################################

ES_FFMPEG_VERSION = 7.1.2
ES_FFMPEG_SOURCE = ffmpeg-$(ES_FFMPEG_VERSION).tar.xz
ES_FFMPEG_SITE = https://ffmpeg.org/releases
ES_FFMPEG_INSTALL_STAGING = YES

ES_FFMPEG_LICENSE = LGPL-2.1+, libjpeg license
ES_FFMPEG_LICENSE_FILES = LICENSE.md COPYING.LGPLv2.1

ES_FFMPEG_CPE_ID_VENDOR = ffmpeg

ES_FFMPEG_CONF_OPTS = \
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

ES_FFMPEG_CONF_OPTS += --libdir=/usr/lib/es-ffmpeg

ES_FFMPEG_DEPENDENCIES += host-pkgconf

ES_FFMPEG_CONF_OPTS += --disable-gpl
ES_FFMPEG_CONF_OPTS += --disable-nonfree
ES_FFMPEG_CONF_OPTS += --disable-ffmpeg
ES_FFMPEG_CONF_OPTS += --disable-ffplay
ES_FFMPEG_CONF_OPTS += --disable-libjack
ES_FFMPEG_CONF_OPTS += --disable-libpulse
ES_FFMPEG_CONF_OPTS += --disable-ffprobe
ES_FFMPEG_CONF_OPTS += --disable-libxcb
ES_FFMPEG_CONF_OPTS += --disable-postproc
ES_FFMPEG_CONF_OPTS += --disable-encoders
ES_FFMPEG_CONF_OPTS += --disable-muxers
ES_FFMPEG_CONF_OPTS += --disable-libfdk-aac
ES_FFMPEG_CONF_OPTS += --disable-gnutls
ES_FFMPEG_CONF_OPTS += --disable-openssl
ES_FFMPEG_CONF_OPTS += --disable-libopencv

ifeq ($(BR2_PACKAGE_LIBV4L),y)
ES_FFMPEG_DEPENDENCIES += libv4l
ES_FFMPEG_CONF_OPTS += --enable-libv4l2
else
ES_FFMPEG_CONF_OPTS += --disable-libv4l2
endif

ifeq ($(BR2_PACKAGE_ES_FFMPEG_SWSCALE),y)
ES_FFMPEG_CONF_OPTS += --enable-swscale
else
ES_FFMPEG_CONF_OPTS += --disable-swscale
endif

ifneq ($(call qstrip,$(BR2_PACKAGE_ES_FFMPEG_DECODERS)),all)
ES_FFMPEG_CONF_OPTS += --disable-decoders \
	$(foreach x,$(call qstrip,$(BR2_PACKAGE_ES_FFMPEG_DECODERS)),--enable-decoder=$(x))
endif

ifneq ($(call qstrip,$(BR2_PACKAGE_ES_FFMPEG_DEMUXERS)),all)
ES_FFMPEG_CONF_OPTS += --disable-demuxers \
	$(foreach x,$(call qstrip,$(BR2_PACKAGE_ES_FFMPEG_DEMUXERS)),--enable-demuxer=$(x))
endif

ifneq ($(call qstrip,$(BR2_PACKAGE_ES_FFMPEG_PARSERS)),all)
ES_FFMPEG_CONF_OPTS += --disable-parsers \
	$(foreach x,$(call qstrip,$(BR2_PACKAGE_ES_FFMPEG_PARSERS)),--enable-parser=$(x))
endif

ifneq ($(call qstrip,$(BR2_PACKAGE_ES_FFMPEG_BSFS)),all)
ES_FFMPEG_CONF_OPTS += --disable-bsfs \
	$(foreach x,$(call qstrip,$(BR2_PACKAGE_ES_FFMPEG_BSFS)),--enable-bsf=$(x))
endif


ifneq ($(call qstrip,$(BR2_PACKAGE_ES_FFMPEG_FILTERS)),all)
ES_FFMPEG_CONF_OPTS += --disable-filters \
	$(foreach x,$(call qstrip,$(BR2_PACKAGE_ES_FFMPEG_FILTERS)),--enable-filter=$(x))
endif

ifeq ($(BR2_PACKAGE_ES_FFMPEG_INDEVS),y)
ES_FFMPEG_CONF_OPTS += --enable-indevs
ES_FFMPEG_CONF_OPTS += --disable-alsa
else
ES_FFMPEG_CONF_OPTS += --disable-indevs
endif

ifeq ($(BR2_PACKAGE_ES_FFMPEG_OUTDEVS),y)
ES_FFMPEG_CONF_OPTS += --enable-outdevs
ifeq ($(BR2_PACKAGE_ALSA_LIB),y)
ES_FFMPEG_DEPENDENCIES += alsa-lib
endif
else
ES_FFMPEG_CONF_OPTS += --disable-outdevs
endif

ifeq ($(BR2_TOOLCHAIN_HAS_THREADS),y)
ES_FFMPEG_CONF_OPTS += --enable-pthreads
else
ES_FFMPEG_CONF_OPTS += --disable-pthreads
endif

ifeq ($(BR2_PACKAGE_ZLIB),y)
ES_FFMPEG_CONF_OPTS += --enable-zlib
ES_FFMPEG_DEPENDENCIES += zlib
else
ES_FFMPEG_CONF_OPTS += --disable-zlib
endif

ifeq ($(BR2_PACKAGE_BZIP2),y)
ES_FFMPEG_CONF_OPTS += --enable-bzlib
ES_FFMPEG_DEPENDENCIES += bzip2
else
ES_FFMPEG_CONF_OPTS += --disable-bzlib
endif


ifeq ($(BR2_PACKAGE_ES_FFMPEG_GPL)$(BR2_PACKAGE_LIBCDIO_PARANOIA),yy)
ES_FFMPEG_CONF_OPTS += --enable-libcdio
ES_FFMPEG_DEPENDENCIES += libcdio-paranoia
else
ES_FFMPEG_CONF_OPTS += --disable-libcdio
endif

ifeq ($(BR2_PACKAGE_LIBDRM),y)
ES_FFMPEG_CONF_OPTS += --enable-libdrm
ES_FFMPEG_DEPENDENCIES += libdrm
else
ES_FFMPEG_CONF_OPTS += --disable-libdrm
endif

ifeq ($(BR2_PACKAGE_LIBOPENH264),y)
ES_FFMPEG_CONF_OPTS += --enable-libopenh264
ES_FFMPEG_DEPENDENCIES += libopenh264
else
ES_FFMPEG_CONF_OPTS += --disable-libopenh264
endif

ifeq ($(BR2_PACKAGE_LIBVORBIS),y)
ES_FFMPEG_DEPENDENCIES += libvorbis
ES_FFMPEG_CONF_OPTS += \
	--enable-libvorbis \
	--enable-muxer=ogg \
	--enable-encoder=libvorbis
endif

# REG
ifeq ($(BR2_PACKAGE_LIBV4L),y)
ES_FFMPEG_CONF_OPTS += --enable-v4l2-request
ES_FFMPEG_DEPENDENCIES += libv4l
else
ES_FFMPEG_CONF_OPTS += --disable-v4l2-request
endif

ifeq ($(BR2_PACKAGE_LIBVA),y)
ES_FFMPEG_CONF_OPTS += --enable-vaapi
ES_FFMPEG_DEPENDENCIES += libva
else
ES_FFMPEG_CONF_OPTS += --disable-vaapi
endif

ifeq ($(BR2_PACKAGE_LIBVDPAU),y)
ES_FFMPEG_CONF_OPTS += --enable-vdpau
ES_FFMPEG_DEPENDENCIES += libvdpau
else
ES_FFMPEG_CONF_OPTS += --disable-vdpau
endif

ifeq ($(BR2_PACKAGE_RPI_USERLAND),y)
ES_FFMPEG_CONF_OPTS += --enable-omx --enable-omx-rpi \
	--extra-cflags=-I$(STAGING_DIR)/usr/include/IL
ES_FFMPEG_DEPENDENCIES += rpi-userland
ifeq ($(BR2_arm),y)
ES_FFMPEG_CONF_OPTS += --enable-mmal
else
ES_FFMPEG_CONF_OPTS += --disable-mmal
endif
else
ES_FFMPEG_CONF_OPTS += --disable-mmal --disable-omx --disable-omx-rpi
endif

ifeq ($(BR2_PACKAGE_OPUS),y)
ES_FFMPEG_CONF_OPTS += --enable-libopus
ES_FFMPEG_DEPENDENCIES += opus
else
ES_FFMPEG_CONF_OPTS += --disable-libopus
endif

ifeq ($(BR2_PACKAGE_LIBVPX),y)
ES_FFMPEG_CONF_OPTS += --enable-libvpx
ES_FFMPEG_DEPENDENCIES += libvpx
else
ES_FFMPEG_CONF_OPTS += --disable-libvpx
endif

ifeq ($(BR2_PACKAGE_LIBASS),y)
ES_FFMPEG_CONF_OPTS += --enable-libass
ES_FFMPEG_DEPENDENCIES += libass
else
ES_FFMPEG_CONF_OPTS += --disable-libass
endif

ifeq ($(BR2_PACKAGE_LIBBLURAY),y)
ES_FFMPEG_CONF_OPTS += --enable-libbluray
ES_FFMPEG_DEPENDENCIES += libbluray
else
ES_FFMPEG_CONF_OPTS += --disable-libbluray
endif

ifeq ($(BR2_PACKAGE_LIBVPL),y)
ES_FFMPEG_CONF_OPTS += --enable-libvpl --disable-libmfx
ES_FFMPEG_DEPENDENCIES += libvpl
else ifeq ($(BR2_PACKAGE_INTEL_MEDIASDK),y)
ES_FFMPEG_CONF_OPTS += --disable-libvpl --enable-libmfx
ES_FFMPEG_DEPENDENCIES += intel-mediasdk
else
ES_FFMPEG_CONF_OPTS += --disable-libvpl --disable-libmfx
endif

ES_FFMPEG_CONF_OPTS += --disable-librtmp

ifeq ($(BR2_PACKAGE_LAME),y)
ES_FFMPEG_CONF_OPTS += --enable-libmp3lame
ES_FFMPEG_DEPENDENCIES += lame
else
ES_FFMPEG_CONF_OPTS += --disable-libmp3lame
endif

ifeq ($(BR2_PACKAGE_LIBMODPLUG),y)
ES_FFMPEG_CONF_OPTS += --enable-libmodplug
ES_FFMPEG_DEPENDENCIES += libmodplug
else
ES_FFMPEG_CONF_OPTS += --disable-libmodplug
endif

ifeq ($(BR2_PACKAGE_LIBOPENMPT),y)
ES_FFMPEG_CONF_OPTS += --enable-libopenmpt
ES_FFMPEG_DEPENDENCIES += libopenmpt
else
ES_FFMPEG_CONF_OPTS += --disable-libopenmpt
endif

ifeq ($(BR2_PACKAGE_LIBSOXR),y)
ES_FFMPEG_CONF_OPTS += --enable-libsoxr
ES_FFMPEG_DEPENDENCIES += libsoxr
else
ES_FFMPEG_CONF_OPTS += --disable-libsoxr
endif

ifeq ($(BR2_PACKAGE_SPEEX),y)
ES_FFMPEG_CONF_OPTS += --enable-libspeex
ES_FFMPEG_DEPENDENCIES += speex
else
ES_FFMPEG_CONF_OPTS += --disable-libspeex
endif

ifeq ($(BR2_PACKAGE_LIBTHEORA),y)
ES_FFMPEG_CONF_OPTS += --enable-libtheora
ES_FFMPEG_DEPENDENCIES += libtheora
else
ES_FFMPEG_CONF_OPTS += --disable-libtheora
endif

ifeq ($(BR2_PACKAGE_LIBICONV),y)
ES_FFMPEG_CONF_OPTS += --enable-iconv
ES_FFMPEG_DEPENDENCIES += libiconv
else
ES_FFMPEG_CONF_OPTS += --disable-iconv
endif

ifeq ($(BR2_PACKAGE_LIBXML2),y)
ES_FFMPEG_CONF_OPTS += --enable-libxml2
ES_FFMPEG_DEPENDENCIES += libxml2
else
ES_FFMPEG_CONF_OPTS += --disable-libxml2
endif

# ffmpeg freetype support require fenv.h which is only
# available/working on glibc.
# The microblaze variant doesn't provide the needed exceptions
ifeq ($(BR2_PACKAGE_FREETYPE)$(BR2_TOOLCHAIN_USES_GLIBC)x$(BR2_microblaze),yyx)
ES_FFMPEG_CONF_OPTS += --enable-libfreetype
ES_FFMPEG_DEPENDENCIES += freetype
else
ES_FFMPEG_CONF_OPTS += --disable-libfreetype
endif

ifeq ($(BR2_PACKAGE_FONTCONFIG),y)
ES_FFMPEG_CONF_OPTS += --enable-fontconfig
ES_FFMPEG_DEPENDENCIES += fontconfig
else
ES_FFMPEG_CONF_OPTS += --disable-fontconfig
endif

ifeq ($(BR2_PACKAGE_HARFBUZZ),y)
ES_FFMPEG_CONF_OPTS += --enable-libharfbuzz
ES_FFMPEG_DEPENDENCIES += harfbuzz
else
ES_FFMPEG_CONF_OPTS += --disable-libharfbuzz
endif

ifeq ($(BR2_PACKAGE_LIBFRIBIDI),y)
ES_FFMPEG_CONF_OPTS += --enable-libfribidi
ES_FFMPEG_DEPENDENCIES += libfribidi
else
ES_FFMPEG_CONF_OPTS += --disable-libfribidi
endif

ifeq ($(BR2_PACKAGE_OPENJPEG),y)
ES_FFMPEG_CONF_OPTS += --enable-libopenjpeg
ES_FFMPEG_DEPENDENCIES += openjpeg
else
ES_FFMPEG_CONF_OPTS += --disable-libopenjpeg
endif

ES_FFMPEG_CONF_OPTS += --disable-libx264
ES_FFMPEG_CONF_OPTS += --disable-libx265

ifeq ($(BR2_PACKAGE_DAV1D),y)
ES_FFMPEG_CONF_OPTS += --enable-libdav1d
ES_FFMPEG_DEPENDENCIES += dav1d
else
ES_FFMPEG_CONF_OPTS += --disable-libdav1d
endif

ifeq ($(BR2_X86_CPU_HAS_MMX),y)
ES_FFMPEG_CONF_OPTS += --enable-x86asm
ES_FFMPEG_DEPENDENCIES += host-nasm
else
ES_FFMPEG_CONF_OPTS += --disable-x86asm
ES_FFMPEG_CONF_OPTS += --disable-mmx
endif

ifeq ($(BR2_X86_CPU_HAS_SSE),y)
ES_FFMPEG_CONF_OPTS += --enable-sse
else
ES_FFMPEG_CONF_OPTS += --disable-sse
endif

ifeq ($(BR2_X86_CPU_HAS_SSE2),y)
ES_FFMPEG_CONF_OPTS += --enable-sse2
else
ES_FFMPEG_CONF_OPTS += --disable-sse2
endif

ifeq ($(BR2_X86_CPU_HAS_SSE3),y)
ES_FFMPEG_CONF_OPTS += --enable-sse3
else
ES_FFMPEG_CONF_OPTS += --disable-sse3
endif

ifeq ($(BR2_X86_CPU_HAS_SSSE3),y)
ES_FFMPEG_CONF_OPTS += --enable-ssse3
else
ES_FFMPEG_CONF_OPTS += --disable-ssse3
endif

ifeq ($(BR2_X86_CPU_HAS_SSE4),y)
ES_FFMPEG_CONF_OPTS += --enable-sse4
else
ES_FFMPEG_CONF_OPTS += --disable-sse4
endif

ifeq ($(BR2_X86_CPU_HAS_SSE42),y)
ES_FFMPEG_CONF_OPTS += --enable-sse42
else
ES_FFMPEG_CONF_OPTS += --disable-sse42
endif

ifeq ($(BR2_X86_CPU_HAS_AVX),y)
ES_FFMPEG_CONF_OPTS += --enable-avx
else
ES_FFMPEG_CONF_OPTS += --disable-avx
endif

ifeq ($(BR2_X86_CPU_HAS_AVX2),y)
ES_FFMPEG_CONF_OPTS += --enable-avx2
else
ES_FFMPEG_CONF_OPTS += --disable-avx2
endif

# Explicitly disable everything that doesn't match for ARM
# FFMPEG "autodetects" by compiling an extended instruction via AS
# This works on compilers that aren't built for generic by default
ifeq ($(BR2_ARM_CPU_ARMV4),y)
ES_FFMPEG_CONF_OPTS += --disable-armv5te
endif
ifeq ($(BR2_ARM_CPU_ARMV6)$(BR2_ARM_CPU_ARMV7A),y)
ES_FFMPEG_CONF_OPTS += --enable-armv6
else
ES_FFMPEG_CONF_OPTS += --disable-armv6 --disable-armv6t2
endif
ifeq ($(BR2_ARM_CPU_HAS_VFPV2),y)
ES_FFMPEG_CONF_OPTS += --enable-vfp
else
ES_FFMPEG_CONF_OPTS += --disable-vfp
endif
ifeq ($(BR2_ARM_CPU_HAS_NEON),y)
ES_FFMPEG_CONF_OPTS += --enable-neon
else ifeq ($(BR2_aarch64),y)
ES_FFMPEG_CONF_OPTS += --enable-neon
else
ES_FFMPEG_CONF_OPTS += --disable-neon
endif

ifeq ($(BR2_mips)$(BR2_mipsel)$(BR2_mips64)$(BR2_mips64el),y)
ifeq ($(BR2_MIPS_SOFT_FLOAT),y)
ES_FFMPEG_CONF_OPTS += --disable-mipsfpu
else
ES_FFMPEG_CONF_OPTS += --enable-mipsfpu
endif

# Fix build failure on several missing assembly instructions
ES_FFMPEG_CONF_OPTS += --disable-asm
endif # MIPS

ifeq ($(BR2_POWERPC_CPU_HAS_ALTIVEC):$(BR2_powerpc64le),y:)
ES_FFMPEG_CONF_OPTS += --enable-altivec
else ifeq ($(BR2_POWERPC_CPU_HAS_VSX):$(BR2_powerpc64le),y:y)
# On LE, ffmpeg AltiVec support needs VSX intrinsics, and VSX
# is an extension to AltiVec.
ES_FFMPEG_CONF_OPTS += --enable-altivec
else
ES_FFMPEG_CONF_OPTS += --disable-altivec
endif

# Fix build failure on several missing assembly instructions
ifeq ($(BR2_RISCV_32),y)
ES_FFMPEG_CONF_OPTS += --disable-rvv --disable-asm
endif

# Uses __atomic_fetch_add_4
ifeq ($(BR2_TOOLCHAIN_HAS_LIBATOMIC),y)
ES_FFMPEG_CONF_OPTS += --extra-libs=-latomic
endif

ifeq ($(BR2_STATIC_LIBS),)
ES_FFMPEG_CONF_OPTS += --enable-pic
else
ES_FFMPEG_CONF_OPTS += --disable-pic
endif

# Default to --cpu=generic for MIPS architecture, in order to avoid a
# warning from ffmpeg's configure script.
ifeq ($(BR2_mips)$(BR2_mipsel)$(BR2_mips64)$(BR2_mips64el),y)
ES_FFMPEG_CONF_OPTS += --cpu=generic
else ifneq ($(GCC_TARGET_CPU),)
ES_FFMPEG_CONF_OPTS += --cpu="$(GCC_TARGET_CPU)"
else ifneq ($(GCC_TARGET_ARCH),)
ES_FFMPEG_CONF_OPTS += --cpu="$(GCC_TARGET_ARCH)"
endif

ES_FFMPEG_CFLAGS = $(TARGET_CFLAGS)

ifeq ($(BR2_TOOLCHAIN_HAS_GCC_BUG_85180),y)
ES_FFMPEG_CONF_OPTS += --disable-optimizations
ES_FFMPEG_CFLAGS += -O0
endif

ifeq ($(BR2_TOOLCHAIN_HAS_GCC_BUG_68485),y)
ES_FFMPEG_CONF_OPTS += --disable-optimizations
ES_FFMPEG_CFLAGS += -O0
endif

ifeq ($(BR2_ARM_INSTRUCTIONS_THUMB),y)
ES_FFMPEG_CFLAGS += -marm
endif

ES_FFMPEG_CONF_ENV += CFLAGS="$(ES_FFMPEG_CFLAGS)"
ES_FFMPEG_CONF_OPTS += $(call qstrip,$(BR2_PACKAGE_ES_FFMPEG_EXTRACONF))

# Override ES_FFMPEG_CONFIGURE_CMDS: FFmpeg does not support --target and others
define ES_FFMPEG_CONFIGURE_CMDS
	(cd $(ES_FFMPEG_SRCDIR) && rm -rf config.cache && \
	$(TARGET_CONFIGURE_OPTS) \
	$(TARGET_CONFIGURE_ARGS) \
	$(ES_FFMPEG_CONF_ENV) \
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
		$(ES_FFMPEG_CONF_OPTS) \
	)
endef

define ES_FFMPEG_REMOVE_EXAMPLE_SRC_FILES
	rm -rf $(TARGET_DIR)/usr/share/ffmpeg/examples
endef
ES_FFMPEG_POST_INSTALL_TARGET_HOOKS += ES_FFMPEG_REMOVE_EXAMPLE_SRC_FILES

$(eval $(autotools-package))
