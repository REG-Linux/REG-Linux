################################################################################
#
# REGLINUX-MAME (Prebuilt GroovyMAME + libretro-mame)
#
################################################################################
# Version: 0.266
REGLINUX_MAME_VERSION = 0.266
REGLINUX_MAME_SITE = $(call github,REG-Linux,REG-MAME,$(REGLINUX_MAME_VERSION))
REGLINUX_MAME_LICENSE = MAME

REGLINUX_MAME_ARCH = unknown
# Cortex A7
ifeq ($(BR2_cortex_a7),y)
REGLINUX_MAME_ARCH = bcm2836
# Cortex A9
else ifeq ($(BR2_cortex_a9),y)
REGLINUX_MAME_ARCH = s812
# Cortex A15.A7
else ifeq ($(BR2_cortex_a15_a7),y)
REGLINUX_MAME_ARCH = odroidxu4
# Cortex A17
else ifeq ($(BR2_cortex_a17),y)
REGLINUX_MAME_ARCH = rk3288
# Cortex A53
else ifeq ($(BR2_cortex_a53),y)
REGLINUX_MAME_ARCH = h5
# Cortex A35
else ifeq ($(BR2_cortex_a35),y)
REGLINUX_MAME_ARCH = rk3326
# Cortex A55
else ifeq ($(BR2_cortex_a55),y)
REGLINUX_MAME_ARCH = s905gen3
# Cortex A72
else ifeq ($(BR2_cortex_a72),y)
REGLINUX_MAME_ARCH = bcm2711
# Cortex A72.A53
else ifeq ($(BR2_cortex_a72_a53),y)
REGLINUX_MAME_ARCH = rk3399
# Cortex A73.A53
else ifeq ($(BR2_cortex_a73_a53),y)
REGLINUX_MAME_ARCH = s922x
# Cortex A76
else ifeq ($(BR2_cortex_a76),y)
REGLINUX_MAME_ARCH = bcm2712
# Cortex A76.A55
else ifeq ($(BR2_cortex_a76_a55),y)
REGLINUX_MAME_ARCH = rk3588
# Unknown AArch64 saphira CPU
else ifeq ($(BR2_saphira),y)
REGLINUX_MAME_ARCH = saphira
# RISC-V 64 (rv64gc, aka imafd)
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_JH7110),y)
REGLINUX_MAME_ARCH = visionfive2
# RISC-V 64 with vector extensions (aka imafdv)
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_K1),y)
REGLINUX_MAME_ARCH = bpif3
# X86_64-v3 subarchitecture
else ifeq ($(BR2_x86_64_v3),y)
REGLINUX_MAME_ARCH = x86_64_v3
# X86_64 architecture
else ifeq ($(BR2_x86_64),y)
REGLINUX_MAME_ARCH = x86_64
endif

# Compute the archive source file name
REGLINUX_MAME_SOURCE = reglinux-mame-$(REGLINUX_MAME_VERSION)-$(REGLINUX_MAME_ARCH).tar.gz

define REGLINUX_MAME_DOWNLOAD_ARCHIVE
	echo "Downloading https://github.com/REG-Linux/REG-MAME/releases/download/$(REGLINUX_MAME_VERSION)/$(REGLINUX_MAME_SOURCE)"
	cd $(@D) && wget https://github.com/REG-Linux/REG-MAME/releases/download/$(REGLINUX_MAME_VERSION)/$(REGLINUX_MAME_SOURCE)
endef

REGLINUX_MAME_POST_BUILD_HOOKS = REGLINUX_MAME_DOWNLOAD_ARCHIVE

REGLINUX_MAME_CONF_INIT = $(TARGET_DIR)/usr/share/batocera/datainit/system/configs/mame/

define REGLINUX_MAME_INSTALL_TARGET_CMDS
	# copy the prebuilt stuff to rootfs
	tar xzvf $(@D)/$(REGLINUX_MAME_SOURCE) -C $(TARGET_DIR)

	# delete the archive from this directory
	rm $(@D)/$(REGLINUX_MAME_SOURCE)

	# gameStop script when exiting a rotated screen
	mkdir -p $(TARGET_DIR)/usr/share/batocera/configgen/scripts
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/emulators/mame/rotation_fix.sh $(TARGET_DIR)/usr/share/batocera/configgen/scripts/rotation_fix.sh

	# Copy user -autoboot_command overrides (batocera.linux/batocera.linux#11706)
	mkdir -p $(MAME_CONF_INIT)/autoload
	cp -R $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/emulators/mame/autoload	$(MAME_CONF_INIT)
endef

define REGLINUX_MAME_EVMAPY
	mkdir -p $(TARGET_DIR)/usr/share/evmapy
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/emulators/mame/mame.mame.keys $(TARGET_DIR)/usr/share/evmapy
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/emulators/mame/mame.mame.keys $(TARGET_DIR)/usr/share/evmapy/mame.keys
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/emulators/mame/mame.mame.keys $(TARGET_DIR)/usr/share/evmapy/adam.mame.keys
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/emulators/mame/mame.mame.keys $(TARGET_DIR)/usr/share/evmapy/advision.mame.keys
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/emulators/mame/mame.mame.keys $(TARGET_DIR)/usr/share/evmapy/apfm1000.mame.keys
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/emulators/mame/mame.mame.keys $(TARGET_DIR)/usr/share/evmapy/apple2.mame.keys
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/emulators/mame/mame.mame.keys $(TARGET_DIR)/usr/share/evmapy/apple2gs.mame.keys
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/emulators/mame/mame.mame.keys $(TARGET_DIR)/usr/share/evmapy/arcadia.mame.keys
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/emulators/mame/mame.mame.keys $(TARGET_DIR)/usr/share/evmapy/archimedes.mame.keys
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/emulators/mame/mame.mame.keys $(TARGET_DIR)/usr/share/evmapy/astrocde.mame.keys
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/emulators/mame/mame.mame.keys $(TARGET_DIR)/usr/share/evmapy/atom.mame.keys
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/emulators/mame/mame.mame.keys $(TARGET_DIR)/usr/share/evmapy/bbc.mame.keys
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/emulators/mame/mame.mame.keys $(TARGET_DIR)/usr/share/evmapy/camplynx.mame.keys
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/emulators/mame/mame.mame.keys $(TARGET_DIR)/usr/share/evmapy/cdi.mame.keys
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/emulators/mame/mame.mame.keys $(TARGET_DIR)/usr/share/evmapy/coco.mame.keys
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/emulators/mame/mame.mame.keys $(TARGET_DIR)/usr/share/evmapy/crvision.mame.keys
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/emulators/mame/mame.mame.keys $(TARGET_DIR)/usr/share/evmapy/electron.mame.keys
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/emulators/mame/mame.mame.keys $(TARGET_DIR)/usr/share/evmapy/fm7.mame.keys
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/emulators/mame/mame.mame.keys $(TARGET_DIR)/usr/share/evmapy/fmtowns.mame.keys
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/emulators/mame/mame.mame.keys $(TARGET_DIR)/usr/share/evmapy/gamate.mame.keys
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/emulators/mame/mame.mame.keys $(TARGET_DIR)/usr/share/evmapy/gameandwatch.mame.keys
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/emulators/mame/mame.mame.keys $(TARGET_DIR)/usr/share/evmapy/gamecom.mame.keys
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/emulators/mame/mame.mame.keys $(TARGET_DIR)/usr/share/evmapy/gamepock.mame.keys
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/emulators/mame/mame.mame.keys $(TARGET_DIR)/usr/share/evmapy/gmaster.mame.keys
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/emulators/mame/mame.mame.keys $(TARGET_DIR)/usr/share/evmapy/gp32.mame.keys
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/emulators/mame/mame.mame.keys $(TARGET_DIR)/usr/share/evmapy/lcdgames.mame.keys
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/emulators/mame/mame.mame.keys $(TARGET_DIR)/usr/share/evmapy/laser310.mame.keys
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/emulators/mame/mame.mame.keys $(TARGET_DIR)/usr/share/evmapy/macintosh.mame.keys
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/emulators/mame/mame.mame.keys $(TARGET_DIR)/usr/share/evmapy/megaduck.mame.keys
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/emulators/mame/mame.mame.keys $(TARGET_DIR)/usr/share/evmapy/neogeo.mame.keys
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/emulators/mame/mame.mame.keys $(TARGET_DIR)/usr/share/evmapy/pdp1.mame.keys
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/emulators/mame/mame.mame.keys $(TARGET_DIR)/usr/share/evmapy/plugnplay.mame.keys
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/emulators/mame/mame.mame.keys $(TARGET_DIR)/usr/share/evmapy/pv1000.mame.keys
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/emulators/mame/mame.mame.keys $(TARGET_DIR)/usr/share/evmapy/socrates.mame.keys
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/emulators/mame/mame.mame.keys $(TARGET_DIR)/usr/share/evmapy/supracan.mame.keys
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/emulators/mame/mame.mame.keys $(TARGET_DIR)/usr/share/evmapy/ti99.mame.keys
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/emulators/mame/mame.mame.keys $(TARGET_DIR)/usr/share/evmapy/tutor.mame.keys
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/emulators/mame/mame.mame.keys $(TARGET_DIR)/usr/share/evmapy/vc4000.mame.keys
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/emulators/mame/mame.mame.keys $(TARGET_DIR)/usr/share/evmapy/vectrex.mame.keys
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/emulators/mame/mame.mame.keys $(TARGET_DIR)/usr/share/evmapy/vgmplay.mame.keys
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/emulators/mame/mame.mame.keys $(TARGET_DIR)/usr/share/evmapy/vsmile.mame.keys
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/emulators/mame/mame.mame.keys $(TARGET_DIR)/usr/share/evmapy/xegs.mame.keys
endef

REGLINUX_MAME_POST_INSTALL_TARGET_HOOKS += REGLINUX_MAME_EVMAPY

$(eval $(generic-package))
