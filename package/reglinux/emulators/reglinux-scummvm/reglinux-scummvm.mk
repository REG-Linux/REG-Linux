################################################################################
#
# scummvm
#
################################################################################
# Version: 2.8.1 - "Oh MMy!"
REGLINUX_SCUMMVM_VERSION = v2.8.1
REGLINUX_SCUMMVM_SITE = $(call github,REG-Linux,REG-ScummVM,$(REGLINUX_SCUMMVM_VERSION))
REGLINUX_SCUMMVM_LICENSE = GPLv2

REGLINUX_SCUMMVM_ARCH = unknown
# JZ4770
ifeq ($(BR2_mips_xburst),y)
REGLINUX_SCUMMVM_ARCH = jz4770
# ARM1176
else ifeq ($(BR2_arm1176jzf_s),y)
REGLINUX_SCUMMVM_ARCH = bcm2835
# Cortex A7
else ifeq ($(BR2_cortex_a7),y)
REGLINUX_SCUMMVM_ARCH = bcm2836
# Cortex A9
else ifeq ($(BR2_cortex_a9),y)
REGLINUX_SCUMMVM_ARCH = s812
# Cortex A15.A7
else ifeq ($(BR2_cortex_a15_a7),y)
REGLINUX_SCUMMVM_ARCH = odroidxu4
# Cortex A17
else ifeq ($(BR2_cortex_a17),y)
REGLINUX_SCUMMVM_ARCH = rk3288
# Cortex A53
else ifeq ($(BR2_cortex_a53),y)
REGLINUX_SCUMMVM_ARCH = h5
# Cortex A35
else ifeq ($(BR2_cortex_a35),y)
REGLINUX_SCUMMVM_ARCH = rk3326
# Cortex A55
else ifeq ($(BR2_cortex_a55),y)
REGLINUX_SCUMMVM_ARCH = s905gen3
# Cortex A72
else ifeq ($(BR2_cortex_a72),y)
REGLINUX_SCUMMVM_ARCH = bcm2711
# Cortex A72.A53
else ifeq ($(BR2_cortex_a72_a53),y)
REGLINUX_SCUMMVM_ARCH = rk3399
# Cortex A73.A53
else ifeq ($(BR2_cortex_a73_a53),y)
REGLINUX_SCUMMVM_ARCH = s922x
# Cortex A76
else ifeq ($(BR2_cortex_a76),y)
REGLINUX_SCUMMVM_ARCH = bcm2712
# Cortex A76.A55
else ifeq ($(BR2_cortex_a76_a55),y)
REGLINUX_SCUMMVM_ARCH = rk3588
# Cortex A78.A55
else ifeq ($(BR2_cortex_a78_a55),y)
REGLINUX_SCUMMVM_ARCH = rk3588
# Unknown AArch64 saphira CPU
else ifeq ($(BR2_saphira),y)
REGLINUX_SCUMMVM_ARCH = saphira
# RISC-V 64 (rv64gc, aka imafd)
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_JH7110),y)
REGLINUX_SCUMMVM_ARCH = visionfive2
# RISC-V 64 with vector extensions (aka imafdv)
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_K1),y)
REGLINUX_SCUMMVM_ARCH = bpif3
# X86_64-v3 subarchitecture
else ifeq ($(BR2_x86_64_v3),y)
REGLINUX_SCUMMVM_ARCH = x86_64_v3
# X86_64 architecture
else ifeq ($(BR2_x86_64),y)
REGLINUX_SCUMMVM_ARCH = x86_64
endif

# Compute the archive source file name
REGLINUX_SCUMMVM_SOURCE = reglinux-scummvm-$(REGLINUX_SCUMMVM_VERSION)-$(REGLINUX_SCUMMVM_ARCH).tar.gz

define REGLINUX_SCUMMVM_DOWNLOAD_ARCHIVE
	echo "Downloading https://github.com/REG-Linux/REG-ScummVM/releases/download/$(REGLINUX_SCUMMVM_VERSION)/$(REGLINUX_SCUMMVM_SOURCE)"
	cd $(@D) && wget https://github.com/REG-Linux/REG-ScummVM/releases/download/$(REGLINUX_SCUMMVM_VERSION)/$(REGLINUX_SCUMMVM_SOURCE)
endef

REGLINUX_SCUMMVM_POST_BUILD_HOOKS = REGLINUX_SCUMMVM_DOWNLOAD_ARCHIVE

define REGLINUX_SCUMMVM_INSTALL_TARGET_CMDS
	# copy the prebuilt stuff to rootfs
	tar xzvf $(@D)/$(REGLINUX_SCUMMVM_SOURCE) -C $(TARGET_DIR)

	mkdir -p $(TARGET_DIR)/usr/share/evmapy/
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/emulators/scummvm/scummvm.keys \
        	$(TARGET_DIR)/usr/share/evmapy/
endef

$(eval $(generic-package))
