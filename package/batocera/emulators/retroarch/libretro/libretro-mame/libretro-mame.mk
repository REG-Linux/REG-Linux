################################################################################
#
# libretro-mame
#
################################################################################

# Version : Sep 27, 2024
# lrmame0270
LIBRETRO_MAME_VERSION = lrmame0270
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

ifeq ($(BR2_x86_64),y)
LIBRETRO_MAME_EXTRA_ARGS += PTR64=1 LIBRETRO_CPU=x86_64 PLATFORM=x86_64
else ifeq ($(BR2_i386),y)
LIBRETRO_MAME_EXTRA_ARGS += PTR64=0 LIBRETRO_CPU=x86 PLATFORM=x86
else ifeq ($(BR2_RISCV_64),y)
LIBRETRO_MAME_EXTRA_ARGS += PTR64=1 LIBRETRO_CPU=riscv64 PLATFORM=riscv64
else ifeq ($(BR2_riscv),y)
LIBRETRO_MAME_EXTRA_ARGS += PTR64=0 LIBRETRO_CPU=riscv PLATFORM=riscv
else ifeq ($(BR2_arm),y)
LIBRETRO_MAME_EXTRA_ARGS += PTR64=0 LIBRETRO_CPU=arm PLATFORM=arm
# workaround for linkage failure using ld on arm 32-bit targets
LIBRETRO_MAME_ARCHOPTS += -fuse-ld=gold -Wl,--long-plt
# workaround for asmjit broken build system (arm backend is not public)
LIBRETRO_MAME_ARCHOPTS += -D__arm__ -DASMJIT_BUILD_X86
else ifeq ($(BR2_aarch64),y)
LIBRETRO_MAME_EXTRA_ARGS += PTR64=1 LIBRETRO_CPU= PLATFORM=arm64
# workaround for asmjit broken build system (arm backend is not public)
LIBRETRO_MAME_ARCHOPTS += -D__aarch64__ -DASMJIT_BUILD_X86
endif

# Enforce symbols debugging with O0
ifeq ($(BR2_ENABLE_DEBUG),y)
	LIBRETRO_MAME_EXTRA_ARGS += SYMBOLS=1 SYMLEVEL=2 OPTIMIZE=0
# Stick with O2, too much bloat with O3 !!
else ifeq ($(BR2_x86_64),y)
	LIBRETRO_MAME_EXTRA_ARGS += OPTIMIZE=s LTO=1
else
	LIBRETRO_MAME_EXTRA_ARGS += OPTIMIZE=2 LTO=1
endif

define LIBRETRO_MAME_BUILD_CMDS
	# create some dirs while with parallelism, sometimes it fails because this directory is missing
	mkdir -p $(@D)/build/libretro/obj/x64/libretro/src/osd/libretro/libretro-internal

	# First, we need to build genie for host
	cd $(@D); \
		PATH="$(HOST_DIR)/bin:$$PATH" \
		$(MAKE) TARGETOS=linux OSD=sdl genie \
		TARGET=mame SUBTARGET=tiny \
		NO_USE_PORTAUDIO=1 NO_X11=1 USE_SDL=0 \
		USE_QTDEBUG=0 DEBUG=0 IGNORE_GIT=1 MPARAM=""

	# remove bfm* drivers to save space
	find $(@D)/src/mame/bfm/ -type f | xargs grep -e 'GAME(\|GAMEL' | cut -f 2 -d "," | sort -bu | tr -d "[:blank:]" > $(@D)/games.list
	find $(@D)/src/mame/bfm/ -type f | xargs sed -i '/GAME[L]*(/d'
	# remove skeleton drivers to save space
	find $(@D)/src/mame/ -type f | xargs grep -e 'MACHINE_IS_SKELETON\|MACHINE_MECHANICAL\|MACHINE_FLAGS_MECHANICAL' | grep -v 'define' | grep -v 'setname' | cut -f 1 -d ":" | sort -u > $(@D)/machines1.list
	find $(@D)/src/mame/ -type f | xargs grep -e 'MACHINE_IS_SKELETON\|MACHINE_MECHANICAL\|MACHINE_FLAGS_MECHANICAL' | grep -v 'define' | grep -v 'setname' | cut -f 2 -d "," | sort -bu | tr -d "[:blank:]" >> $(@D)/games.list
	cat $(@D)/machines1.list | while read file ; do sed -i '/define.*MACHINE_IS_SKELETON/p;/setname.*MACHINE_IS_SKELETON/p;/MACHINE_IS_SKELETON/d' $$file ; done
	# do not remove '#define GAME_FLAGS' and other definition lines
	cat $(@D)/machines1.list | while read file ; do sed -i '/define.*MACHINE_MECHANICAL/p;/setname.*MACHINE_MECHANICAL/p;/MACHINE_MECHANICAL/d' $$file ; done
	cat $(@D)/machines1.list | while read file ; do sed -i '/define.*MACHINE_FLAGS_MECHANICAL/p;/setname.*MACHINE_FLAGS_MECHANICAL/p;/MACHINE_FLAGS_MECHANICAL/d' $$file ; done
	# remove remaining MECHANICAL games using 'GAME_FLAGS' label
	find $(@D)/src/mame/ -type f | xargs grep -e 'GAME_FLAGS.*MACHINE_MECHANICAL' | cut -f 1 -d ":" | sort -u > $(@D)/machines2.list
	cat $(@D)/machines2.list | while read file ; do grep 'GAME_FLAGS' $$file | grep -v 'define' | grep -v 'setname' | cut -f 2 -d "," | sort -bu | tr -d "[:blank:]" >> $(@D)/games.list; done
	cat $(@D)/machines2.list | while read file ; do sed -i '/define GAME_FLAGS/p;/setname.*GAME_FLAGS/p;/GAME_FLAGS/d' $$file ; done
	# Remove reference to skeleton|mechanical drivers in mame.lst
	cat $(@D)/games.list | while read file ; do sed -i /$$file/d $(@D)/src/mame/mame.lst ; done

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
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/emulators/mame/blank.fmtowns $(TARGET_DIR)/usr/share/mame/blank.fmtowns

	# Copy coin drop plugin
	mkdir -p $(TARGET_DIR)/usr/bin/mame/
	cp -R -u $(@D)/plugins $(TARGET_DIR)/usr/bin/mame/
	cp -R -u $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/emulators/mame/coindrop $(TARGET_DIR)/usr/bin/mame/plugins
endef

$(eval $(generic-package))
