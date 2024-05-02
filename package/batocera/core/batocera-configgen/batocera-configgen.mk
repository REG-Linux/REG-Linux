################################################################################
#
# batocera-configgen
#
################################################################################

BATOCERA_CONFIGGEN_VERSION = 1.4
BATOCERA_CONFIGGEN_LICENSE = GPL
BATOCERA_CONFIGGEN_SOURCE=
BATOCERA_CONFIGGEN_DEPENDENCIES = python3 python-pyyaml host-nuitka nuitka
BATOCERA_CONFIGGEN_INSTALL_STAGING = YES

CONFIGGEN_DIR = $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/core/batocera-configgen

define BATOCERA_CONFIGGEN_EXTRACT_CMDS
	cp -avf $(CONFIGGEN_DIR)/configgen/* $(@D)
endef

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_BCM2835),y)
	BATOCERA_CONFIGGEN_SYSTEM=bcm2835
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_BCM2836),y)
	BATOCERA_CONFIGGEN_SYSTEM=bcm2836
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_BCM2837),y)
	BATOCERA_CONFIGGEN_SYSTEM=bcm2837
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_BCM2711),y)
	BATOCERA_CONFIGGEN_SYSTEM=bcm2711
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_BCM2712),y)
	BATOCERA_CONFIGGEN_SYSTEM=bcm2712
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_XU4),y)
	BATOCERA_CONFIGGEN_SYSTEM=odroidxu4
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RK3288),y)
	BATOCERA_CONFIGGEN_SYSTEM=rk3288
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_S905),y)
	BATOCERA_CONFIGGEN_SYSTEM=s905
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_S905GEN2),y)
	BATOCERA_CONFIGGEN_SYSTEM=s905gen2
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_S905GEN3),y)
	BATOCERA_CONFIGGEN_SYSTEM=s905gen3
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_S9GEN4),y)
	BATOCERA_CONFIGGEN_SYSTEM=s9gen4
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_X86),y)
	BATOCERA_CONFIGGEN_SYSTEM=x86
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_X86_64_ANY),y)
	BATOCERA_CONFIGGEN_SYSTEM=x86_64
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RK3399),y)
	BATOCERA_CONFIGGEN_SYSTEM=rk3399
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_S922X)$(BR2_PACKAGE_BATOCERA_TARGET_A3GEN2),y)
	BATOCERA_CONFIGGEN_SYSTEM=s922x
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RK3328),y)
	BATOCERA_CONFIGGEN_SYSTEM=rk3328
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RK3568),y)
	BATOCERA_CONFIGGEN_SYSTEM=rk3568
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RK3326),y)
	BATOCERA_CONFIGGEN_SYSTEM=rk3326
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_H3)$(BR2_PACKAGE_BATOCERA_TARGET_CHA),y)
	BATOCERA_CONFIGGEN_SYSTEM=h3
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_H5),y)
	BATOCERA_CONFIGGEN_SYSTEM=h5
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_H616),y)
	BATOCERA_CONFIGGEN_SYSTEM=h616
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_S812),y)
	BATOCERA_CONFIGGEN_SYSTEM=s812
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RK3128),y)
	BATOCERA_CONFIGGEN_SYSTEM=rk3128
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_ODIN),y)
	BATOCERA_CONFIGGEN_SYSTEM=odin
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_H6),y)
	BATOCERA_CONFIGGEN_SYSTEM=h6
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RK3588),y)
	BATOCERA_CONFIGGEN_SYSTEM=rk3588
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RISCV),y)
	BATOCERA_CONFIGGEN_SYSTEM=riscv
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_SAPHIRA),y)
	BATOCERA_CONFIGGEN_SYSTEM=x86_64
endif

define BATOCERA_CONFIGGEN_INSTALL_STAGING_CMDS
	mkdir -p $(STAGING_DIR)/usr/share/batocera/configgen
	cp $(CONFIGGEN_DIR)/configs/configgen-defaults.yml \
	    $(STAGING_DIR)/usr/share/batocera/configgen/configgen-defaults.yml
	cp $(CONFIGGEN_DIR)/configs/configgen-defaults-$(BATOCERA_CONFIGGEN_SYSTEM).yml \
	    $(STAGING_DIR)/usr/share/batocera/configgen/configgen-defaults-arch.yml
endef

define BATOCERA_CONFIGGEN_CONFIGS
	mkdir -p $(TARGET_DIR)/usr/share/batocera/configgen
	cp -pr $(CONFIGGEN_DIR)/data \
	    $(TARGET_DIR)/usr/share/batocera/configgen/
	cp $(CONFIGGEN_DIR)/configs/configgen-defaults.yml \
	    $(TARGET_DIR)/usr/share/batocera/configgen/configgen-defaults.yml
	cp $(CONFIGGEN_DIR)/configs/configgen-defaults-$(BATOCERA_CONFIGGEN_SYSTEM).yml \
	    $(TARGET_DIR)/usr/share/batocera/configgen/configgen-defaults-arch.yml
	cp $(CONFIGGEN_DIR)/scripts/call_achievements_hooks.sh \
	    $(TARGET_DIR)/usr/share/batocera/configgen/
endef

define BATOCERA_CONFIGGEN_BINS
    chmod a+x $(TARGET_DIR)/usr/lib/python$(PYTHON3_VERSION_MAJOR)/site-packages/configgen/emulatorlauncher.py
	(mkdir -p $(TARGET_DIR)/usr/bin/ && cd $(TARGET_DIR)/usr/bin/ && \
	    ln -sf /usr/lib/python$(PYTHON3_VERSION_MAJOR)/site-packages/configgen/emulatorlauncher.py emulatorlauncher)
endef

define BATOCERA_CONFIGGEN_ES_HOOKS
	install -D -m 0755 $(CONFIGGEN_DIR)/scripts/powermode_launch_hooks.sh \
	    $(TARGET_DIR)/usr/share/batocera/configgen/scripts/powermode_launch_hooks.sh
endef

define BATOCERA_CONFIGGEN_X86_HOOKS
	install -D -m 0755 $(CONFIGGEN_DIR)/scripts/tdp_hooks.sh \
	    $(TARGET_DIR)/usr/share/batocera/configgen/scripts/tdp_hooks.sh

	install -D -m 0755 $(CONFIGGEN_DIR)/scripts/nvidia-workaround.sh \
	    $(TARGET_DIR)/usr/share/batocera/configgen/scripts/nvidia-workaround.sh
endef

BATOCERA_CONFIGGEN_POST_INSTALL_TARGET_HOOKS = BATOCERA_CONFIGGEN_CONFIGS
BATOCERA_CONFIGGEN_POST_INSTALL_TARGET_HOOKS += BATOCERA_CONFIGGEN_ES_HOOKS

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_X86_64_ANY),y)
    BATOCERA_CONFIGGEN_POST_INSTALL_TARGET_HOOKS += BATOCERA_CONFIGGEN_X86_HOOKS
endif

BATOCERA_CONFIGGEN_SETUP_TYPE = setuptools

# Cross-compile ABI
# TODO : riscv64
BATOCERA_CONFIGGEN_CROSS_ABI = unknown
ifeq ($(BR2_x86_64),y)
BATOCERA_CONFIGGEN_CROSS_ABI = x86_64-linux-gnu
else ifeq ($(BR2_arm),y)
BATOCERA_CONFIGGEN_CROSS_ABI = arm-linux-gnueabihf
else ifeq ($(BR2_aarch64),y)
BATOCERA_CONFIGGEN_CROSS_ABI = aarch64-linux-gnu
endif

define BATOCERA_CONFIGGEN_CROSS_COMPILE_NUITKA
	$(HOST_DIR)/usr/bin/pip install pyudev
	$(HOST_DIR)/usr/bin/pip install evdev
	$(HOST_DIR)/usr/bin/pip install pillow
	$(HOST_DIR)/usr/bin/pip install ordered-set
	$(HOST_DIR)/usr/bin/pip install zstandard
	$(QEMU_USER) $(TARGET_DIR)/usr/bin/python -m pip install pyudev
	$(QEMU_USER) $(TARGET_DIR)/usr/bin/python -m pip install evdev
	$(QEMU_USER) $(TARGET_DIR)/usr/bin/python -m pip install pillow
	$(QEMU_USER) $(TARGET_DIR)/usr/bin/python -m pip install ordered-set
	cd $(@D)/ && \
	NUITKA_CACHE_DIR=$(HOME)/.buildroot-ccache \
	PYTHONPATH=$(TARGET_DIR)/usr/lib/python3.11 \
	ABI=$(BATOCERA_CONFIGGEN_CROSS_ABI) \
	CC=$(TARGET_CC) LD=$(TARGET_LD) \
	SYSROOT="$(STAGING_DIR)/usr" \
	PATH=$(STAGING_DIR)/usr/bin:$(PATH) \
	QEMU_USER=$(QEMU_USER) \
	$(QEMU_USER) \
	$(TARGET_DIR)/usr/bin/python -m nuitka \
	--python-for-scons=$(HOST_DIR)/usr/bin/python \
	--standalone configgen/emulatorlauncher.py \
	--static-libpython=yes \
	--prefer-source-code

	# Enabling LTO breaks on linker --lto=yes

	#install -D -m 0755 $(@D)/emulatorlauncher.bin $(TARGET_DIR)/usr/bin/emulatorlauncher
	cp -r $(@D)/emulatorlauncher.dist/* $(TARGET_DIR)/usr/bin/
	cd $(TARGET_DIR)/usr/bin && mv emulatorlauncher.bin emulatorlauncher
	rm -rf $(TARGET_DIR)/usr/lib/python3.11/site-packages/nuitka
endef

define BATOCERA_CONFIGGEN_COMPILE_NUITKA
	$(HOST_DIR)/usr/bin/pip install pyudev
	$(HOST_DIR)/usr/bin/pip install evdev
	$(HOST_DIR)/usr/bin/pip install pillow
	$(HOST_DIR)/usr/bin/pip install ordered-set
	$(HOST_DIR)/usr/bin/pip install zstandard
	cd $(@D)/ && \
	QEMU_USER="" \
	PATH=$(STAGING_DIR)/usr/bin:$(PATH) \
	CC=$(TARGET_CC) LD=$(TARGET_LD) \
	SYSROOT="$(STAGING_DIR)/usr" \
	ABI=$(BATOCERA_CONFIGGEN_CROSS_ABI) \
	NUITKA_CACHE_DIR=$(HOME)/.buildroot-ccache \
	$(HOST_DIR)/usr/bin/python -m nuitka \
	--python-for-scons=$(HOST_DIR)/usr/bin/python \
	--standalone configgen/emulatorlauncher.py \
	--static-libpython=yes \
	#--prefer-source-code \

	#--lto=yes
	#PATH=$(HOST_DIR)/usr/bin:$(PATH) \
	#install -D -m 0755 $(@D)/emulatorlauncher.bin $(TARGET_DIR)/usr/bin/emulatorlauncher
	cp -r $(@D)/emulatorlauncher.dist/* $(TARGET_DIR)/usr/bin/
	cd $(TARGET_DIR)/usr/bin && mv emulatorlauncher.bin emulatorlauncher
	rm -rf $(TARGET_DIR)/usr/lib/python3.11/site-packages/nuitka
endef

ifeq ($(BR2_PACKAGE_NUITKA),y)
ifeq ($(BR2_x86_64),y)
BATOCERA_CONFIGGEN_POST_INSTALL_TARGET_HOOKS += BATOCERA_CONFIGGEN_COMPILE_NUITKA
else
BATOCERA_CONFIGGEN_POST_INSTALL_TARGET_HOOKS += BATOCERA_CONFIGGEN_CROSS_COMPILE_NUITKA
endif
else
BATOCERA_CONFIGGEN_POST_INSTALL_TARGET_HOOKS += BATOCERA_CONFIGGEN_BINS
endif

$(eval $(python-package))
