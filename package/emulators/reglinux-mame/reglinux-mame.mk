################################################################################
#
# REGLINUX-MAME (Prebuilt MAME/GroovyMAME + libretro-mame)
#
################################################################################
# Version: GroovyMAME 0.289 / lr-mame 0289. The release tag is the 4-digit
# form the build workflow derives from mame.mk's gmNNNN version string.
REGLINUX_MAME_VERSION = 0289
# Release ASSET, not the github() helper.
REGLINUX_MAME_SITE = https://github.com/REG-Linux/REG-MAME/releases/download/$(REGLINUX_MAME_VERSION)
REGLINUX_MAME_LICENSE = MAME

# The prebuilt is chosen by CPU, not by board.
REGLINUX_MAME_ARCH = unknown
# Cortex A35 (rk3326, s9gen4)
ifeq ($(BR2_cortex_a35),y)
REGLINUX_MAME_ARCH = cortex_a35
# Cortex A53 (a133, bcm2837, h616, h700, rk3328, s905, s905gen2, sun50i)
else ifeq ($(BR2_cortex_a53),y)
REGLINUX_MAME_ARCH = cortex_a53
# Cortex A55 (odroidc5, rk3568, s905gen3, t527)
else ifeq ($(BR2_cortex_a55),y)
REGLINUX_MAME_ARCH = cortex_a55
# Cortex A57 (l4t)
else ifeq ($(BR2_cortex_a57),y)
REGLINUX_MAME_ARCH = cortex_a57
# Cortex A72 (bcm2711)
else ifeq ($(BR2_cortex_a72),y)
REGLINUX_MAME_ARCH = cortex_a72
# Cortex A72.A53 (rk3399, rk3576 and variants)
else ifeq ($(BR2_cortex_a72_a53),y)
REGLINUX_MAME_ARCH = cortex_a72_a53
# Cortex A73.A53 (a3gen2, s922x, sm6115)
else ifeq ($(BR2_cortex_a73_a53),y)
REGLINUX_MAME_ARCH = cortex_a73_a53
# Cortex A75.A55 (sdm845)
else ifeq ($(BR2_cortex_a75_a55),y)
REGLINUX_MAME_ARCH = cortex_a75_a55
# Cortex A76 (bcm2712)
else ifeq ($(BR2_cortex_a76),y)
REGLINUX_MAME_ARCH = cortex_a76
# Cortex A76.A55 (mt8395, qcs6490, rk3588, sm8250)
else ifeq ($(BR2_cortex_a76_a55),y)
REGLINUX_MAME_ARCH = cortex_a76_a55
# Cortex X3 (sm8550)
else ifeq ($(BR2_cortex_x3),y)
REGLINUX_MAME_ARCH = cortex_x3
# Saphira (asahi)
else ifeq ($(BR2_saphira),y)
REGLINUX_MAME_ARCH = saphira
# RISC-V has no CPU symbol that separates these two, and they are not interchangeable
else ifeq ($(BR2_PACKAGE_SYSTEM_TARGET_K1)$(BR2_PACKAGE_SYSTEM_TARGET_K3),y)
REGLINUX_MAME_ARCH = riscv_rvv
else ifeq ($(BR2_PACKAGE_SYSTEM_TARGET_JH7110)$(BR2_PACKAGE_SYSTEM_TARGET_TH1520),y)
REGLINUX_MAME_ARCH = riscv
# x86-64-v3 must be tested before x86_64: both are set on that board
else ifeq ($(BR2_x86_x86_64_v3),y)
REGLINUX_MAME_ARCH = x86_64_v3
else ifeq ($(BR2_x86_64),y)
REGLINUX_MAME_ARCH = x86_64
endif

# Compute the archive source file name
REGLINUX_MAME_SOURCE = reglinux-mame-$(REGLINUX_MAME_VERSION)-$(REGLINUX_MAME_ARCH).tar.xz

# This is a rootfs overlay rooted at target/, not a source tree, so skip the
# extract step and untar straight into TARGET_DIR at install time. Buildroot
# still downloads it to $(REGLINUX_MAME_DL_DIR), so it is cached across builds.
REGLINUX_MAME_EXTRACT_CMDS =

REGLINUX_MAME_CONF_INIT = $(TARGET_DIR)/usr/share/reglinux/datainit/system/configs/mame/

define REGLINUX_MAME_INSTALL_TARGET_CMDS
	# copy the prebuilt stuff to rootfs (members are rooted at target/)
	tar -xJf $(REGLINUX_MAME_DL_DIR)/$(REGLINUX_MAME_SOURCE) -C $(TARGET_DIR)/../

	# remove vgmplay.xml files, symlink hash files
	rm -Rf $(TARGET_DIR)/usr/share/lr-mame/hash
	rm $(TARGET_DIR)/usr/bin/mame/hash/vgmplay.xml
	ln -s /usr/bin/mame/hash $(TARGET_DIR)/usr/share/lr-mame/hash

	# Copy user -autoboot_command overrides
	mkdir -p $(REGLINUX_MAME_CONF_INIT)
	cp -R $(BR2_EXTERNAL_REGLINUX_PATH)/package/emulators/mame/autoload	$(REGLINUX_MAME_CONF_INIT)
endef

$(eval $(generic-package))
