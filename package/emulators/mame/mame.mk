################################################################################
#
# MAME (GroovyMAME)
#
################################################################################
# Version: GroovyMAME 0.277 - Switchres 2.21e
#MAME_VERSION = gm0277sr221e
#MAME_SITE = $(call github,antonioginer,GroovyMAME,$(MAME_VERSION))
# Version: MAME 0.279
MAME_VERSION = mame0279
MAME_SITE = $(call github,mamedev,MAME,$(MAME_VERSION))
MAME_DEPENDENCIES = sdl2 sdl2_ttf zlib libpng fontconfig sqlite jpeg flac rapidjson expat glm alsa-lib
MAME_LICENSE = MAME

MAME_CROSS_ARCH = unknown
MAME_CROSS_OPTS = PRECOMPILE=0
MAME_CFLAGS =
MAME_LDFLAGS =

MAME_SUBTARGET=mame
MAME_SUFFIX=

# Limit number of jobs not to eat too much RAM....
MAME_MAX_JOBS = 32
MAME_JOBS = $(shell if [ $(PARALLEL_JOBS) -gt $(MAME_MAX_JOBS) ]; then echo $(MAME_MAX_JOBS); else echo $(PARALLEL_JOBS); fi)

# Set PTR64 always on we do not build for 32-bit architectures
MAME_CROSS_OPTS += PTR64=1
MAME_EXTRA_ARGS += PTR64=1
ifeq ($(BR2_x86_64),y)
MAME_EXTRA_ARGS += PLATFORM=x86
else ifeq ($(BR2_aarch64),y)
MAME_EXTRA_ARGS += PLATFORM=arm64 ARCHITECTURE=
else ifeq ($(BR2_RISCV_64),y)
MAME_EXTRA_ARGS += PLATFORM=riscv64 FORCE_DRC_C_BACKEND=1 ARCHITECTURE=
endif

# All platforms run Wayland, no X11
MAME_CROSS_OPTS += NO_X11=1 NO_USE_XINPUT=1 USE_WAYLAND=1
MAME_CFLAGS += -DEGL_NO_X11=1
# No error on unused function
MAME_CFLAGS += -Wno-error=unused-function

# Disable OpenGL if we don't have it
ifneq ($(BR2_PACKAGE_HAS_LIBGL),y)
MAME_CROSS_OPTS += NO_OPENGL=1 NO_USE_BGFX_KHRONOS=1
endif

# Handle alsa vs pulse/pipewire audio stack
ifeq ($(BR2_PACKAGE_PULSEAUDIO),y)
MAME_DEPENDENCIES += pulseaudio
else
MAME_CROSS_OPTS += NO_USE_PULSEAUDIO=1
endif

# Define cross-architecture, adjust DRC backend
ifeq ($(BR2_x86_64),y)
MAME_CROSS_ARCH = x86_64
else ifeq ($(BR2_aarch64),y)
MAME_CROSS_ARCH = arm64
# AArch64 CPU flags
ifeq ($(BR2_cortex_a53),y)
MAME_CFLAGS += -mcpu=cortex-a53 -mtune=cortex-a53
else ifeq ($(BR2_cortex_a35),y)
MAME_CFLAGS += -mcpu=cortex-a35 -mtune=cortex-a35
else ifeq ($(BR2_cortex_a55),y)
MAME_CFLAGS += -mcpu=cortex-a55 -mtune=cortex-a55
else ifeq ($(BR2_cortex_a73_a53),y)
MAME_CFLAGS += -mcpu=cortex-a73.cortex-a53 -mtune=cortex-a73.cortex-a53
else ifeq ($(BR2_cortex_a72),y)
MAME_CFLAGS += -mcpu=cortex-a72 -mtune=cortex-a72
else ifeq ($(BR2_cortex_a76),y)
MAME_CFLAGS += -mcpu=cortex-a76 -mtune=cortex-a76
else ifeq ($(BR2_cortex_a76_a55),y)
MAME_CFLAGS += -mcpu=cortex-a76.cortex-a55 -mtune=cortex-a76.cortex-a55
endif
else
MAME_CROSS_OPTS += FORCE_DRC_C_BACKEND=1
endif

# Handle RV64GC platform (can be further tweaked and optimized)
ifeq ($(BR2_RISCV_64),y)
MAME_CROSS_ARCH = riscv64
# Cast alignment warnings cause errors on riscv64
MAME_CFLAGS += -mabi=lp64d -malign-data=xlen -Wno-error=cast-align
# Use large code model to avoid linking relocation errors
MAME_CFLAGS += -mcmodel=large
MAME_LDFLAGS += -mcmodel=large
# Proper architecture flags for JH7110
MAME_CFLAGS += -march=rv64gc_zba_zbb -mcpu=sifive-u74 -mtune=sifive-u74
endif

# Enforce symbols debugging with O0
ifeq ($(BR2_ENABLE_DEBUG),y)
	MAME_EXTRA_ARGS += SYMBOLS=1 SYMLEVEL=2 OPTIMIZE=0
# Stick with Os on x86_64 too much bloat with O2/O3 !!
#else ifeq ($(BR2_x86_64),y)
#	MAME_EXTRA_ARGS += OPTIMIZE=s LTO=1
# Use O2 no LTO for RISC-V
#else ifeq ($(BR2_riscv),y)
#	MAME_EXTRA_ARGS += OPTIMIZE=2
# Use O3 with LTO on other archs
else
# Stick to O2 + LTO to limit binary footprint
	MAME_EXTRA_ARGS += OPTIMIZE=2 LTO=1
endif

define MAME_CONFIGURE_CMDS
	# Prepare
	cd $(@D); \
	cp $(BR2_EXTERNAL_REGLINUX_PATH)/package/emulators/mame/unwanted.txt $(@D)/unwanted.txt ; \
	chmod +x ./prepare.py ; \
	$(HOST_DIR)/bin/python3 ./prepare.py

	# First, we need to build genie for host
	cd $(@D); \
		PATH="$(HOST_DIR)/bin:$$PATH" \
		$(MAKE) TARGETOS=linux OSD=sdl genie \
		TARGET=mame SUBTARGET=tiny \
		NO_USE_PORTAUDIO=1 NO_X11=1 USE_SDL=0 \
		USE_QTDEBUG=0 DEBUG=0 IGNORE_GIT=1 MPARAM=""
endef

define MAME_BUILD_CMDS
	# Compile emulation target (MAME)
	cd $(@D); \
	PATH="$(HOST_DIR)/bin:$$PATH" \
	SYSROOT="$(STAGING_DIR)" \
	CFLAGS="--sysroot=$(STAGING_DIR) $(MAME_CFLAGS) -fpch-preprocess"   \
	LDFLAGS="--sysroot=$(STAGING_DIR) $(MAME_LDFLAGS)"  MPARAM="" \
	PKG_CONFIG="$(HOST_DIR)/usr/bin/pkg-config --define-prefix" \
	PKG_CONFIG_PATH="$(STAGING_DIR)/usr/lib/pkgconfig" \
	CCACHE_SLOPPINESS="pch_defines,time_macros,include_file_ctime,include_file_mtime" \
	$(MAKE) -j$(MAME_JOBS) TARGETOS=linux OSD=sdl \
	TARGET=mame \
	SUBTARGET=$(MAME_SUBTARGET) \
	OVERRIDE_CC="$(TARGET_CC)" \
	OVERRIDE_CXX="$(TARGET_CXX)" \
	OVERRIDE_LD="$(TARGET_LD)" \
	OVERRIDE_AR="$(TARGET_AR)" \
	OVERRIDE_STRIP="$(TARGET_STRIP)" \
	$(MAME_EXTRA_ARGS) \
	CROSS_BUILD=1 \
	CROSS_ARCH="$(MAME_CROSS_ARCH)" \
	$(MAME_CROSS_OPTS) \
	NO_USE_PORTAUDIO=1 \
	USE_SYSTEM_LIB_ZLIB=1 \
	USE_SYSTEM_LIB_JPEG=1 \
	USE_SYSTEM_LIB_FLAC=1 \
	USE_SYSTEM_LIB_SQLITE3=1 \
	USE_SYSTEM_LIB_RAPIDJSON=1 \
	USE_SYSTEM_LIB_EXPAT=1 \
	USE_SYSTEM_LIB_GLM=1 \
	OPENMP=1 \
	SDL_INSTALL_ROOT="$(STAGING_DIR)/usr" USE_LIBSDL=1 \
	USE_QTDEBUG=0 DEBUG=0 IGNORE_GIT=1 \
	REGENIE=1 \
	LDOPTS="-lasound -lfontconfig" \
	SYMBOLS=0 \
	STRIP_SYMBOLS=1 \
	TOOLS=1
endef

MAME_CONF_INIT = $(TARGET_DIR)/usr/share/reglinux/datainit/system/configs/mame/

define MAME_INSTALL_TARGET_CMDS
	# Create specific directories on target to store MAME distro
	mkdir -p $(TARGET_DIR)/usr/bin/mame/
	mkdir -p $(TARGET_DIR)/usr/bin/mame/ctrlr
	mkdir -p $(TARGET_DIR)/usr/bin/mame/docs/legal
	mkdir -p $(TARGET_DIR)/usr/bin/mame/docs/man
	mkdir -p $(TARGET_DIR)/usr/bin/mame/docs/swlist
	mkdir -p $(TARGET_DIR)/usr/bin/mame/hash
	mkdir -p $(TARGET_DIR)/usr/bin/mame/ini/examples
	mkdir -p $(TARGET_DIR)/usr/bin/mame/ini/presets
	mkdir -p $(TARGET_DIR)/usr/bin/mame/language
	mkdir -p $(TARGET_DIR)/usr/bin/mame/roms

	# Install binaries and default distro
	$(INSTALL) -D $(@D)/mame$(MAME_SUFFIX)	$(TARGET_DIR)/usr/bin/mame/mame
	cp $(@D)/COPYING			$(TARGET_DIR)/usr/bin/mame/
	cp $(@D)/README.md			$(TARGET_DIR)/usr/bin/mame/
	cp $(@D)/uismall.bdf		$(TARGET_DIR)/usr/bin/mame/
	cp -R $(@D)/artwork			$(TARGET_DIR)/usr/bin/mame/
	cp -R $(@D)/bgfx			$(TARGET_DIR)/usr/bin/mame/
	cp -R $(@D)/hash			$(TARGET_DIR)/usr/bin/mame/
	cp -R $(@D)/hlsl			$(TARGET_DIR)/usr/bin/mame/
	cp -R $(@D)/ini				$(TARGET_DIR)/usr/bin/mame/
	cp -R $(@D)/keymaps			$(TARGET_DIR)/usr/bin/mame/
	cp -R $(@D)/language		$(TARGET_DIR)/usr/bin/mame/
	cp -R -u $(@D)/plugins			$(TARGET_DIR)/usr/bin/mame/
	# Skip regression tests
	#cp -R $(@D)/regtests		$(TARGET_DIR)/usr/bin/mame/
	cp -R $(@D)/roms			$(TARGET_DIR)/usr/bin/mame/
	cp -R $(@D)/samples			$(TARGET_DIR)/usr/bin/mame/
	cp -R $(@D)/web				$(TARGET_DIR)/usr/bin/mame/

	# MAME tools
	$(INSTALL) -D $(@D)/castool		$(TARGET_DIR)/usr/bin/mame/
	$(INSTALL) -D $(@D)/chdman		$(TARGET_DIR)/usr/bin/mame/
	$(INSTALL) -D $(@D)/floptool	$(TARGET_DIR)/usr/bin/mame/
	$(INSTALL) -D $(@D)/imgtool		$(TARGET_DIR)/usr/bin/mame/
	$(INSTALL) -D $(@D)/jedutil		$(TARGET_DIR)/usr/bin/mame/
	$(INSTALL) -D $(@D)/ldresample	$(TARGET_DIR)/usr/bin/mame/
	$(INSTALL) -D $(@D)/ldverify	$(TARGET_DIR)/usr/bin/mame/
	$(INSTALL) -D $(@D)/romcmp		$(TARGET_DIR)/usr/bin/mame/

	# MAME dev tools skipped
	#$(INSTALL) -D $(@D)/unidasm	$(TARGET_DIR)/usr/bin/mame/
	#$(INSTALL) -D $(@D)/nltool		$(TARGET_DIR)/usr/bin/mame/
	#$(INSTALL) -D $(@D)/nlwav		$(TARGET_DIR)/usr/bin/mame/

	# Delete .po translation files
	find $(TARGET_DIR)/usr/bin/mame/language -name "*.po" -type f -delete

	# Delete bgfx shaders for DX9/DX11/Metal
	rm -Rf $(TARGET_DIR)/usr/bin/mame/bgfx/shaders/metal/
	rm -Rf $(TARGET_DIR)/usr/bin/mame/bgfx/shaders/dx11/
	rm -Rf $(TARGET_DIR)/usr/bin/mame/bgfx/shaders/dx9/

	# Copy extra bgfx shaders
	cp $(BR2_EXTERNAL_REGLINUX_PATH)/package/emulators/mame/crt-geom-deluxe-rgb.json $(TARGET_DIR)/usr/bin/mame/bgfx/chains
	cp $(BR2_EXTERNAL_REGLINUX_PATH)/package/emulators/mame/crt-geom-deluxe-composite.json $(TARGET_DIR)/usr/bin/mame/bgfx/chains

	# Copy blank disk image(s)
	mkdir -p $(TARGET_DIR)/usr/share/mame
	cp $(BR2_EXTERNAL_REGLINUX_PATH)/package/emulators/mame/blank.fmtowns $(TARGET_DIR)/usr/share/mame/blank.fmtowns

	# Copy coin drop plugin
	cp -R -u $(BR2_EXTERNAL_REGLINUX_PATH)/package/emulators/mame/coindrop $(TARGET_DIR)/usr/bin/mame/plugins

	# Copy data plugin information
	mkdir -p $(TARGET_DIR)/usr/bin/mame/dats
	cp -R $(BR2_EXTERNAL_REGLINUX_PATH)/package/emulators/mame/dats                         $(TARGET_DIR)/usr/bin/mame/dats/
	mkdir -p $(TARGET_DIR)/usr/bin/mame/history
	gunzip -c $(BR2_EXTERNAL_REGLINUX_PATH)/package/emulators/mame/history/history.xml.gz > $(TARGET_DIR)/usr/bin/mame/history/history.xml

	# gameStop script when exiting a rotated screen
	mkdir -p $(TARGET_DIR)/usr/share/reglinux/configgen/scripts
	cp $(BR2_EXTERNAL_REGLINUX_PATH)/package/emulators/mame/rotation_fix.sh $(TARGET_DIR)/usr/share/reglinux/configgen/scripts/rotation_fix.sh

	# Copy user -autoboot_command overrides (batocera.linux/batocera.linux#11706)
	mkdir -p $(MAME_CONF_INIT)/autoload
	cp -R $(BR2_EXTERNAL_REGLINUX_PATH)/package/emulators/mame/autoload			$(MAME_CONF_INIT)
endef

define MAME_EVMAPY
	mkdir -p $(TARGET_DIR)/usr/share/evmapy
	cp $(BR2_EXTERNAL_REGLINUX_PATH)/package/emulators/mame/mame.mame.keys $(TARGET_DIR)/usr/share/evmapy
	cp $(BR2_EXTERNAL_REGLINUX_PATH)/package/emulators/mame/mame.mame.keys $(TARGET_DIR)/usr/share/evmapy/mame.keys
	cp $(BR2_EXTERNAL_REGLINUX_PATH)/package/emulators/mame/mame.mame.keys $(TARGET_DIR)/usr/share/evmapy/adam.mame.keys
	cp $(BR2_EXTERNAL_REGLINUX_PATH)/package/emulators/mame/mame.mame.keys $(TARGET_DIR)/usr/share/evmapy/advision.mame.keys
	cp $(BR2_EXTERNAL_REGLINUX_PATH)/package/emulators/mame/mame.mame.keys $(TARGET_DIR)/usr/share/evmapy/apfm1000.mame.keys
	cp $(BR2_EXTERNAL_REGLINUX_PATH)/package/emulators/mame/mame.mame.keys $(TARGET_DIR)/usr/share/evmapy/apple2.mame.keys
	cp $(BR2_EXTERNAL_REGLINUX_PATH)/package/emulators/mame/mame.mame.keys $(TARGET_DIR)/usr/share/evmapy/apple2gs.mame.keys
	cp $(BR2_EXTERNAL_REGLINUX_PATH)/package/emulators/mame/mame.mame.keys $(TARGET_DIR)/usr/share/evmapy/arcadia.mame.keys
	cp $(BR2_EXTERNAL_REGLINUX_PATH)/package/emulators/mame/mame.mame.keys $(TARGET_DIR)/usr/share/evmapy/archimedes.mame.keys
	cp $(BR2_EXTERNAL_REGLINUX_PATH)/package/emulators/mame/mame.mame.keys $(TARGET_DIR)/usr/share/evmapy/astrocde.mame.keys
	cp $(BR2_EXTERNAL_REGLINUX_PATH)/package/emulators/mame/mame.mame.keys $(TARGET_DIR)/usr/share/evmapy/atom.mame.keys
	cp $(BR2_EXTERNAL_REGLINUX_PATH)/package/emulators/mame/mame.mame.keys $(TARGET_DIR)/usr/share/evmapy/bbc.mame.keys
	cp $(BR2_EXTERNAL_REGLINUX_PATH)/package/emulators/mame/mame.mame.keys $(TARGET_DIR)/usr/share/evmapy/camplynx.mame.keys
	cp $(BR2_EXTERNAL_REGLINUX_PATH)/package/emulators/mame/mame.mame.keys $(TARGET_DIR)/usr/share/evmapy/cdi.mame.keys
	cp $(BR2_EXTERNAL_REGLINUX_PATH)/package/emulators/mame/mame.mame.keys $(TARGET_DIR)/usr/share/evmapy/coco.mame.keys
	cp $(BR2_EXTERNAL_REGLINUX_PATH)/package/emulators/mame/mame.mame.keys $(TARGET_DIR)/usr/share/evmapy/crvision.mame.keys
	cp $(BR2_EXTERNAL_REGLINUX_PATH)/package/emulators/mame/mame.mame.keys $(TARGET_DIR)/usr/share/evmapy/electron.mame.keys
	cp $(BR2_EXTERNAL_REGLINUX_PATH)/package/emulators/mame/mame.mame.keys $(TARGET_DIR)/usr/share/evmapy/fm7.mame.keys
	cp $(BR2_EXTERNAL_REGLINUX_PATH)/package/emulators/mame/mame.mame.keys $(TARGET_DIR)/usr/share/evmapy/fmtowns.mame.keys
	cp $(BR2_EXTERNAL_REGLINUX_PATH)/package/emulators/mame/mame.mame.keys $(TARGET_DIR)/usr/share/evmapy/gamate.mame.keys
	cp $(BR2_EXTERNAL_REGLINUX_PATH)/package/emulators/mame/mame.mame.keys $(TARGET_DIR)/usr/share/evmapy/gameandwatch.mame.keys
	cp $(BR2_EXTERNAL_REGLINUX_PATH)/package/emulators/mame/mame.mame.keys $(TARGET_DIR)/usr/share/evmapy/gamecom.mame.keys
	cp $(BR2_EXTERNAL_REGLINUX_PATH)/package/emulators/mame/mame.mame.keys $(TARGET_DIR)/usr/share/evmapy/gamepock.mame.keys
	cp $(BR2_EXTERNAL_REGLINUX_PATH)/package/emulators/mame/mame.mame.keys $(TARGET_DIR)/usr/share/evmapy/gmaster.mame.keys
	cp $(BR2_EXTERNAL_REGLINUX_PATH)/package/emulators/mame/mame.mame.keys $(TARGET_DIR)/usr/share/evmapy/gp32.mame.keys
	cp $(BR2_EXTERNAL_REGLINUX_PATH)/package/emulators/mame/mame.mame.keys $(TARGET_DIR)/usr/share/evmapy/lcdgames.mame.keys
	cp $(BR2_EXTERNAL_REGLINUX_PATH)/package/emulators/mame/mame.mame.keys $(TARGET_DIR)/usr/share/evmapy/laser310.mame.keys
	cp $(BR2_EXTERNAL_REGLINUX_PATH)/package/emulators/mame/mame.mame.keys $(TARGET_DIR)/usr/share/evmapy/macintosh.mame.keys
	cp $(BR2_EXTERNAL_REGLINUX_PATH)/package/emulators/mame/mame.mame.keys $(TARGET_DIR)/usr/share/evmapy/megaduck.mame.keys
	cp $(BR2_EXTERNAL_REGLINUX_PATH)/package/emulators/mame/mame.mame.keys $(TARGET_DIR)/usr/share/evmapy/neogeo.mame.keys
	cp $(BR2_EXTERNAL_REGLINUX_PATH)/package/emulators/mame/mame.mame.keys $(TARGET_DIR)/usr/share/evmapy/pdp1.mame.keys
	cp $(BR2_EXTERNAL_REGLINUX_PATH)/package/emulators/mame/mame.mame.keys $(TARGET_DIR)/usr/share/evmapy/plugnplay.mame.keys
	cp $(BR2_EXTERNAL_REGLINUX_PATH)/package/emulators/mame/mame.mame.keys $(TARGET_DIR)/usr/share/evmapy/pv1000.mame.keys
	cp $(BR2_EXTERNAL_REGLINUX_PATH)/package/emulators/mame/mame.mame.keys $(TARGET_DIR)/usr/share/evmapy/socrates.mame.keys
	cp $(BR2_EXTERNAL_REGLINUX_PATH)/package/emulators/mame/mame.mame.keys $(TARGET_DIR)/usr/share/evmapy/supracan.mame.keys
	cp $(BR2_EXTERNAL_REGLINUX_PATH)/package/emulators/mame/mame.mame.keys $(TARGET_DIR)/usr/share/evmapy/ti99.mame.keys
	cp $(BR2_EXTERNAL_REGLINUX_PATH)/package/emulators/mame/mame.mame.keys $(TARGET_DIR)/usr/share/evmapy/tutor.mame.keys
	cp $(BR2_EXTERNAL_REGLINUX_PATH)/package/emulators/mame/mame.mame.keys $(TARGET_DIR)/usr/share/evmapy/vc4000.mame.keys
	cp $(BR2_EXTERNAL_REGLINUX_PATH)/package/emulators/mame/mame.mame.keys $(TARGET_DIR)/usr/share/evmapy/vectrex.mame.keys
	cp $(BR2_EXTERNAL_REGLINUX_PATH)/package/emulators/mame/mame.mame.keys $(TARGET_DIR)/usr/share/evmapy/vsmile.mame.keys
	cp $(BR2_EXTERNAL_REGLINUX_PATH)/package/emulators/mame/mame.mame.keys $(TARGET_DIR)/usr/share/evmapy/xegs.mame.keys
endef

MAME_POST_INSTALL_TARGET_HOOKS += MAME_EVMAPY

$(eval $(generic-package))
