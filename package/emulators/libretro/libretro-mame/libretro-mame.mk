################################################################################
#
# libretro-mame
#
################################################################################
# Version lrmame0279 : Aug 3, 2025
LIBRETRO_MAME_VERSION = lrmame0279
LIBRETRO_MAME_SITE = $(call github,libretro,mame,$(LIBRETRO_MAME_VERSION))
LIBRETRO_MAME_LICENSE = MAME

LIBRETRO_MAME_DEPENDENCIES = alsa-lib

# Disable pulseaudio if not built
ifeq ($(BR2_PACKAGE_PULSEAUDIO),y)
LIBRETRO_MAME_DEPENDENCIES += pulseaudio
else
LIBRETRO_MAME_EXTRA_ARGS += NO_USE_PULSEAUDIO=1
endif

# Limit number of jobs not to eat too much RAM....
LIBRETRO_MAME_MAX_JOBS = 32
LIBRETRO_MAME_JOBS = $(shell if [ $(PARALLEL_JOBS) -gt $(LIBRETRO_MAME_MAX_JOBS) ]; then echo $(LIBRETRO_MAME_MAX_JOBS); else echo $(PARALLEL_JOBS); fi)

LIBRETRO_MAME_EXTRA_ARGS += PTR64=1
ifeq ($(BR2_x86_64),y)
LIBRETRO_MAME_EXTRA_ARGS += LIBRETRO_CPU=x86_64 PLATFORM=x86
else ifeq ($(BR2_aarch64),y)
LIBRETRO_MAME_EXTRA_ARGS += LIBRETRO_CPU=arm64 PLATFORM=arm64 ARCHITECTURE=
else ifeq ($(BR2_RISCV_64),y)
LIBRETRO_MAME_EXTRA_ARGS += LIBRETRO_CPU=riscv64 PLATFORM=riscv64 FORCE_DRC_C_BACKEND=1 ARCHITECTURE=
endif

# Enforce symbols debugging with O0
ifeq ($(BR2_ENABLE_DEBUG),y)
	LIBRETRO_MAME_EXTRA_ARGS += SYMBOLS=1 SYMLEVEL=2 OPTIMIZE=0
# Stick with O2 or Os, too much bloat with O3 !!
else
	LIBRETRO_MAME_EXTRA_ARGS += OPTIMIZE=2 LTO=1
endif

define LIBRETRO_MAME_BUILD_CMDS
	# Prepare
	cd $(@D); \
        cp $(BR2_EXTERNAL_REGLINUX_PATH)/package/emulators/libretro/libretro-mame/unwanted.txt $(@D)/unwanted.txt ; \
	chmod +x ./prepare.py ; \
	$(HOST_DIR)/bin/python3 ./prepare.py

	# create some dirs while with parallelism, sometimes it fails because this directory is missing
	mkdir -p $(@D)/build/libretro/obj/x64/libretro/src/osd/libretro/libretro-internal

	# First, we need to build genie for host
	cd $(@D); \
		PATH="$(HOST_DIR)/bin:$$PATH" \
		$(MAKE) TARGETOS=linux OSD=sdl genie \
		TARGET=mame SUBTARGET=tiny \
		NO_USE_PORTAUDIO=1 NO_X11=1 USE_SDL=0 \
		USE_QTDEBUG=0 DEBUG=0 IGNORE_GIT=1 MPARAM=""

	# Compile
	CCACHE_SLOPPINESS="pch_defines,time_macros,include_file_ctime,include_file_mtime" \
	$(MAKE) -j$(LIBRETRO_MAME_JOBS) -C $(@D)/ OPENMP=1 REGENIE=1 VERBOSE=1 NOWERROR=1 PYTHON_EXECUTABLE=python3 \
		CONFIG=libretro LIBRETRO_OS="unix" ARCH="" PROJECT="" ARCHOPTS="$(LIBRETRO_MAME_ARCHOPTS)" \
		DISTRO="debian-stable" OVERRIDE_CC="$(TARGET_CC)" OVERRIDE_CXX="$(TARGET_CXX)"             \
		OVERRIDE_LD="$(TARGET_LD)" RANLIB="$(TARGET_RANLIB)" AR="$(TARGET_AR)"                     \
		$(LIBRETRO_MAME_EXTRA_ARGS) CROSS_BUILD=1 TARGET="mame" SUBTARGET="mame" RETRO=1           \
		OSD="retro" DEBUG=0 LDOPTS="-lasound"
endef

define LIBRETRO_MAME_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/mame_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/mame_libretro.so
	mkdir -p $(TARGET_DIR)/usr/share/lr-mame/hash
	cp -R $(@D)/hash $(TARGET_DIR)/usr/share/lr-mame

	mkdir -p $(TARGET_DIR)/usr/share/mame
	cp $(BR2_EXTERNAL_REGLINUX_PATH)/package/emulators/mame/blank.fmtowns $(TARGET_DIR)/usr/share/mame/blank.fmtowns

	# Copy coin drop plugin
	mkdir -p $(TARGET_DIR)/usr/bin/mame/
	cp -R -u $(@D)/plugins $(TARGET_DIR)/usr/bin/mame/
	cp -R -u $(BR2_EXTERNAL_REGLINUX_PATH)/package/emulators/mame/coindrop $(TARGET_DIR)/usr/bin/mame/plugins
endef

$(eval $(generic-package))
