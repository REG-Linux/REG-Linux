################################################################################
#
# libretro-same-cdi
#
################################################################################
# Version: Commits on Apr 4, 2025
LIBRETRO_SAME_CDI_VERSION = f1ae7c8341a075ea977c703ae2f47de42878f7be
LIBRETRO_SAME_CDI_SITE = $(call github,REG-Linux,libretro-cdi,$(LIBRETRO_SAME_CDI_VERSION))
LIBRETRO_SAME_CDI_LICENSE = GPL

LIBRETRO_SAME_CDI_MAX_JOBS = 6
LIBRETRO_SAME_CDI_JOBS = $(shell if [ $(PARALLEL_JOBS) -gt $(LIBRETRO_SAME_CDI_MAX_JOBS) ]; then echo $(LIBRETRO_SAME_CDI_MAX_JOBS); else echo $(PARALLEL_JOBS); fi)

ifeq ($(BR2_x86_64),y)
LIBRETRO_SAME_CDI_EXTRA_ARGS += LIBRETRO_CPU=x86_64 PLATFORM=x64
else ifeq ($(BR2_aarch64),y)
LIBRETRO_SAME_CDI_EXTRA_ARGS += PTR64=1 LIBRETRO_CPU= PLATFORM=arm64 ARCHITECTURE= NOASM=1
else ifeq ($(BR2_RISCV_64),y)
LIBRETRO_SAME_CDI_EXTRA_ARGS += LIBRETRO_CPU=riscv64 PLATFORM=riscv64
endif
LIBRETRO_SAME_CDI_EXTRA_ARGS += PTR64=1

define LIBRETRO_SAME_CDI_BUILD_CMDS
	# First, we need to build genie for host
	cd $(@D); \
	PATH="$(HOST_DIR)/bin:$$PATH" \
	CCACHE_SLOPPINESS="pch_defines,time_macros,include_file_ctime,include_file_mtime" \
	$(MAKE) TARGETOS=linux OSD=sdl genie \
	TARGET=mame SUBTARGET=tiny \
	NO_USE_PORTAUDIO=1 NO_X11=1 USE_SDL=0 \
	USE_QTDEBUG=0 DEBUG=0 IGNORE_GIT=1 MPARAM=""

	# Then build lr-same-cdi for target
	$(TARGET_CONFIGURE_OPTS) $(MAKE) -j$(LIBRETRO_SAME_CDI_JOBS) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" \
	$(LIBRETRO_SAME_CDI_EXTRA_ARGS) \
	GIT_VERSION="" -C $(@D) -f Makefile.libretro
endef

define LIBRETRO_SAME_CDI_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/same_cdi_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/same_cdi_libretro.so
endef

$(eval $(generic-package))
