################################################################################
#
# reglinux-configgen
#
################################################################################

REGLINUX_CONFIGGEN_VERSION = 0.0.8
REGLINUX_CONFIGGEN_LICENSE = GPL
REGLINUX_CONFIGGEN_SOURCE=
REGLINUX_CONFIGGEN_SETUP_TYPE = pep517
REGLINUX_CONFIGGEN_DEPENDENCIES = \
	python3 \
	python-pyyaml \
	python-lxml \
	python-ruamel-yaml \
	python-toml \
	python-pillow \
	python-evdev \
	python-pyudev \
	python3-configobj \
	ffmpeg-python \
	python-requests
REGLINUX_CONFIGGEN_INSTALL_STAGING = YES

CONFIGGEN_DIR = $(BR2_EXTERNAL_REGLINUX_PATH)/package/system/reglinux-configgen

define REGLINUX_CONFIGGEN_EXTRACT_CMDS
	cp -avf $(CONFIGGEN_DIR)/configgen/* $(@D)
endef

ifeq ($(BR2_PACKAGE_SYSTEM_TARGET_BCM2835),y)
	REGLINUX_CONFIGGEN_SYSTEM=bcm2835
else ifeq ($(BR2_PACKAGE_SYSTEM_TARGET_BCM2836),y)
	REGLINUX_CONFIGGEN_SYSTEM=bcm2836
else ifeq ($(BR2_PACKAGE_SYSTEM_TARGET_BCM2837),y)
	REGLINUX_CONFIGGEN_SYSTEM=bcm2837
else ifeq ($(BR2_PACKAGE_SYSTEM_TARGET_BCM2711),y)
	REGLINUX_CONFIGGEN_SYSTEM=bcm2711
else ifeq ($(BR2_PACKAGE_SYSTEM_TARGET_BCM2712),y)
	REGLINUX_CONFIGGEN_SYSTEM=bcm2712
else ifeq ($(BR2_PACKAGE_SYSTEM_TARGET_XU4),y)
	REGLINUX_CONFIGGEN_SYSTEM=odroidxu4
else ifeq ($(BR2_PACKAGE_SYSTEM_TARGET_RK3288),y)
	REGLINUX_CONFIGGEN_SYSTEM=rk3288
else ifeq ($(BR2_PACKAGE_SYSTEM_TARGET_S905),y)
	REGLINUX_CONFIGGEN_SYSTEM=s905
else ifeq ($(BR2_PACKAGE_SYSTEM_TARGET_S905GEN2),y)
	REGLINUX_CONFIGGEN_SYSTEM=s905gen2
else ifeq ($(BR2_PACKAGE_SYSTEM_TARGET_S905GEN3),y)
	REGLINUX_CONFIGGEN_SYSTEM=s905gen3
else ifeq ($(BR2_PACKAGE_SYSTEM_TARGET_T527),y)
	REGLINUX_CONFIGGEN_SYSTEM=t527
else ifeq ($(BR2_PACKAGE_SYSTEM_TARGET_S9GEN4),y)
	REGLINUX_CONFIGGEN_SYSTEM=s9gen4
else ifeq ($(BR2_PACKAGE_SYSTEM_TARGET_X86),y)
	REGLINUX_CONFIGGEN_SYSTEM=x86
else ifeq ($(BR2_PACKAGE_SYSTEM_TARGET_X86_64_ANY),y)
	REGLINUX_CONFIGGEN_SYSTEM=x86_64
else ifeq ($(BR2_PACKAGE_SYSTEM_TARGET_RK3399),y)
	REGLINUX_CONFIGGEN_SYSTEM=rk3399
else ifeq ($(BR2_PACKAGE_SYSTEM_TARGET_S922X),y)
	REGLINUX_CONFIGGEN_SYSTEM=s922x
else ifeq ($(BR2_PACKAGE_SYSTEM_TARGET_A3GEN2),y)
	REGLINUX_CONFIGGEN_SYSTEM=a3gen2
else ifeq ($(BR2_PACKAGE_SYSTEM_TARGET_RK3328),y)
	REGLINUX_CONFIGGEN_SYSTEM=rk3328
else ifeq ($(BR2_PACKAGE_SYSTEM_TARGET_RK3568),y)
	REGLINUX_CONFIGGEN_SYSTEM=rk3568
else ifeq ($(BR2_PACKAGE_SYSTEM_TARGET_RK3326),y)
	REGLINUX_CONFIGGEN_SYSTEM=rk3326
else ifeq ($(BR2_PACKAGE_SYSTEM_TARGET_H3),y)
	REGLINUX_CONFIGGEN_SYSTEM=h3
else ifeq ($(BR2_PACKAGE_SYSTEM_TARGET_CHA),y)
	REGLINUX_CONFIGGEN_SYSTEM=cha
else ifeq ($(BR2_PACKAGE_SYSTEM_TARGET_H5),y)
	REGLINUX_CONFIGGEN_SYSTEM=h5
else ifeq ($(BR2_PACKAGE_SYSTEM_TARGET_H616),y)
	REGLINUX_CONFIGGEN_SYSTEM=h616
else ifeq ($(BR2_PACKAGE_SYSTEM_TARGET_H700),y)
	REGLINUX_CONFIGGEN_SYSTEM=h700
else ifeq ($(BR2_PACKAGE_SYSTEM_TARGET_S812),y)
	REGLINUX_CONFIGGEN_SYSTEM=s812
else ifeq ($(BR2_PACKAGE_SYSTEM_TARGET_RK3128),y)
	REGLINUX_CONFIGGEN_SYSTEM=rk3128
else ifeq ($(BR2_PACKAGE_SYSTEM_TARGET_ODIN),y)
	REGLINUX_CONFIGGEN_SYSTEM=odin
else ifeq ($(BR2_PACKAGE_SYSTEM_TARGET_SM8250),y)
	REGLINUX_CONFIGGEN_SYSTEM=sm8250
else ifeq ($(BR2_PACKAGE_SYSTEM_TARGET_SM8550),y)
	REGLINUX_CONFIGGEN_SYSTEM=sm8550
else ifeq ($(BR2_PACKAGE_SYSTEM_TARGET_H6),y)
	REGLINUX_CONFIGGEN_SYSTEM=h6
else ifeq ($(BR2_PACKAGE_SYSTEM_TARGET_RK3588),y)
	REGLINUX_CONFIGGEN_SYSTEM=rk3588
else ifeq ($(BR2_PACKAGE_SYSTEM_TARGET_JH7110),y)
	REGLINUX_CONFIGGEN_SYSTEM=jh7110
else ifeq ($(BR2_PACKAGE_SYSTEM_TARGET_K1),y)
	REGLINUX_CONFIGGEN_SYSTEM=k1
else ifeq ($(BR2_PACKAGE_SYSTEM_TARGET_TH1520),y)
	REGLINUX_CONFIGGEN_SYSTEM=th1520
else ifeq ($(BR2_PACKAGE_SYSTEM_TARGET_ASAHI),y)
	REGLINUX_CONFIGGEN_SYSTEM=asahi
else ifeq ($(BR2_PACKAGE_SYSTEM_TARGET_JZ4770),y)
	REGLINUX_CONFIGGEN_SYSTEM=jz4770
else ifeq ($(BR2_PACKAGE_SYSTEM_TARGET_MT8395),y)
	REGLINUX_CONFIGGEN_SYSTEM=mt8395
endif

define REGLINUX_CONFIGGEN_INSTALL_STAGING_CMDS
	mkdir -p $(STAGING_DIR)/usr/share/reglinux/configgen
	cp $(CONFIGGEN_DIR)/configs/configgen-defaults.yml \
	    $(STAGING_DIR)/usr/share/reglinux/configgen/configgen-defaults.yml
	cp $(CONFIGGEN_DIR)/configs/configgen-defaults-$(REGLINUX_CONFIGGEN_SYSTEM).yml \
	    $(STAGING_DIR)/usr/share/reglinux/configgen/configgen-defaults-arch.yml
endef

define REGLINUX_CONFIGGEN_CONFIGS
	mkdir -p $(TARGET_DIR)/usr/share/reglinux/configgen
	cp -pr $(CONFIGGEN_DIR)/data \
	    $(TARGET_DIR)/usr/share/reglinux/configgen/
	cp $(CONFIGGEN_DIR)/configs/configgen-defaults.yml \
	    $(TARGET_DIR)/usr/share/reglinux/configgen/configgen-defaults.yml
	cp $(CONFIGGEN_DIR)/configs/configgen-defaults-$(REGLINUX_CONFIGGEN_SYSTEM).yml \
	    $(TARGET_DIR)/usr/share/reglinux/configgen/configgen-defaults-arch.yml
	cp $(CONFIGGEN_DIR)/scripts/call_achievements_hooks.sh \
	    $(TARGET_DIR)/usr/share/reglinux/configgen/
endef

define REGLINUX_CONFIGGEN_BINS
	chmod a+x $(TARGET_DIR)/usr/lib/python$(PYTHON3_VERSION_MAJOR)/site-packages/configgen/emulatorlauncher.py
	(mkdir -p $(TARGET_DIR)/usr/bin/ && cd $(TARGET_DIR)/usr/bin/ && \
		ln -sf /usr/lib/python$(PYTHON3_VERSION_MAJOR)/site-packages/configgen/emulatorlauncher.py emulatorlauncher)
	if test "$(BR2_PACKAGE_SYSTEM_TARGET_CHA)" = "y" ; then patch "$(TARGET_DIR)/usr/lib/python$(PYTHON3_VERSION_MAJOR)/site-packages/configgen/generators/libretro/libretroConfig.py" < "$(CONFIGGEN_DIR)/force-CHA1-to-Player1-patch-for-CHA"; fi
endef

define REGLINUX_CONFIGGEN_ES_HOOKS
	install -D -m 0755 $(CONFIGGEN_DIR)/scripts/powermode_launch_hooks.sh \
	    $(TARGET_DIR)/usr/share/reglinux/configgen/scripts/powermode_launch_hooks.sh
endef

define REGLINUX_CONFIGGEN_X86_HOOKS
	install -D -m 0755 $(CONFIGGEN_DIR)/scripts/tdp_hooks.sh \
	    $(TARGET_DIR)/usr/share/reglinux/configgen/scripts/tdp_hooks.sh

	install -D -m 0755 $(CONFIGGEN_DIR)/scripts/nvidia-workaround.sh \
	    $(TARGET_DIR)/usr/share/reglinux/configgen/scripts/nvidia-workaround.sh
endef

REGLINUX_CONFIGGEN_POST_INSTALL_TARGET_HOOKS = REGLINUX_CONFIGGEN_CONFIGS
REGLINUX_CONFIGGEN_POST_INSTALL_TARGET_HOOKS += REGLINUX_CONFIGGEN_BINS
REGLINUX_CONFIGGEN_POST_INSTALL_TARGET_HOOKS += REGLINUX_CONFIGGEN_ES_HOOKS

ifeq ($(BR2_PACKAGE_SYSTEM_TARGET_X86_64_ANY),y)
    REGLINUX_CONFIGGEN_POST_INSTALL_TARGET_HOOKS += REGLINUX_CONFIGGEN_X86_HOOKS
endif

$(eval $(python-package))
