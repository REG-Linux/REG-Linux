################################################################################
#
# reglinux-scummvm
#
################################################################################
# Version: the tag REG-ScummVM releases under. The build workflow takes it from
# scummvm.mk's SCUMMVM_VERSION, so the two must agree.
REGLINUX_SCUMMVM_VERSION = v2026.3.0
# Release ASSET, not the github() helper - that one resolves to /archive/ and
# would fetch a repo snapshot instead of the prebuilt tarball.
REGLINUX_SCUMMVM_SITE = https://github.com/REG-Linux/REG-ScummVM/releases/download/$(REGLINUX_SCUMMVM_VERSION)
REGLINUX_SCUMMVM_LICENSE = GPLv2

# The prebuilt is chosen by CPU, not by board: boards sharing a CPU share a
# tarball. Keep this table in step with the matrix in REG-ScummVM's
# build-ScummVM-self-hosted.yml and with prebuild-scummvms.sh.
REGLINUX_SCUMMVM_CPU = unknown
# XBurst (jz4770)
ifeq ($(BR2_mips_xburst),y)
REGLINUX_SCUMMVM_CPU = xburst
# ARM1176 (bcm2835)
else ifeq ($(BR2_arm1176jzf_s),y)
REGLINUX_SCUMMVM_CPU = arm1176jzf_s
# Cortex A7 (bcm2836, cha, h3, mini, rk3128)
else ifeq ($(BR2_cortex_a7),y)
REGLINUX_SCUMMVM_CPU = cortex_a7
# Cortex A9 (de10nano, s812)
else ifeq ($(BR2_cortex_a9),y)
REGLINUX_SCUMMVM_CPU = cortex_a9
# Cortex A15.A7 (odroidxu4)
else ifeq ($(BR2_cortex_a15_a7),y)
REGLINUX_SCUMMVM_CPU = cortex_a15_a7
# Cortex A17 (rk3288)
else ifeq ($(BR2_cortex_a17),y)
REGLINUX_SCUMMVM_CPU = cortex_a17
# Cortex A35 (rk3326, s9gen4)
else ifeq ($(BR2_cortex_a35),y)
REGLINUX_SCUMMVM_CPU = cortex_a35
# Cortex A53 (a133, bcm2837, h616, h700, rk3328, s905, s905gen2, sun50i)
else ifeq ($(BR2_cortex_a53),y)
REGLINUX_SCUMMVM_CPU = cortex_a53
# Cortex A55 (odroidc5, rk3568, s905gen3, t527)
else ifeq ($(BR2_cortex_a55),y)
REGLINUX_SCUMMVM_CPU = cortex_a55
# Cortex A57 (l4t)
else ifeq ($(BR2_cortex_a57),y)
REGLINUX_SCUMMVM_CPU = cortex_a57
# Cortex A72 (bcm2711)
else ifeq ($(BR2_cortex_a72),y)
REGLINUX_SCUMMVM_CPU = cortex_a72
# Cortex A72.A53 (rk3399, rk3576 and variants)
else ifeq ($(BR2_cortex_a72_a53),y)
REGLINUX_SCUMMVM_CPU = cortex_a72_a53
# Cortex A73.A53 (a3gen2, s922x, sm6115)
else ifeq ($(BR2_cortex_a73_a53),y)
REGLINUX_SCUMMVM_CPU = cortex_a73_a53
# Cortex A75.A55 (sdm845)
else ifeq ($(BR2_cortex_a75_a55),y)
REGLINUX_SCUMMVM_CPU = cortex_a75_a55
# Cortex A76 (bcm2712)
else ifeq ($(BR2_cortex_a76),y)
REGLINUX_SCUMMVM_CPU = cortex_a76
# Cortex A76.A55 (mt8395, qcs6490, rk3588, sm8250)
else ifeq ($(BR2_cortex_a76_a55),y)
REGLINUX_SCUMMVM_CPU = cortex_a76_a55
# Cortex X3 (sm8550)
else ifeq ($(BR2_cortex_x3),y)
REGLINUX_SCUMMVM_CPU = cortex_x3
# Saphira (asahi)
else ifeq ($(BR2_saphira),y)
REGLINUX_SCUMMVM_CPU = saphira
# RISC-V has no CPU symbol that separates these two, and they are not
# interchangeable: k1/k3 build with RVV, jh7110/th1520 are plain rv64gc.
else ifeq ($(BR2_PACKAGE_SYSTEM_TARGET_K1)$(BR2_PACKAGE_SYSTEM_TARGET_K3),y)
REGLINUX_SCUMMVM_CPU = riscv_rvv
else ifeq ($(BR2_PACKAGE_SYSTEM_TARGET_JH7110)$(BR2_PACKAGE_SYSTEM_TARGET_TH1520),y)
REGLINUX_SCUMMVM_CPU = riscv
# x86-64-v3 must be tested before x86_64: both are set on that board
else ifeq ($(BR2_x86_x86_64_v3),y)
REGLINUX_SCUMMVM_CPU = x86_64_v3
else ifeq ($(BR2_x86_64),y)
REGLINUX_SCUMMVM_CPU = x86_64
endif

# Compute the archive source file name
REGLINUX_SCUMMVM_SOURCE = reglinux-scummvm-$(REGLINUX_SCUMMVM_VERSION)-$(REGLINUX_SCUMMVM_CPU).tar.xz

# This is a rootfs overlay rooted at target/, not a source tree, so skip the
# extract step and untar straight into TARGET_DIR at install time. Buildroot
# still downloads it to $(REGLINUX_SCUMMVM_DL_DIR), so it is cached across builds.
REGLINUX_SCUMMVM_EXTRACT_CMDS =

define REGLINUX_SCUMMVM_INSTALL_TARGET_CMDS
	# copy the prebuilt stuff to rootfs (members are rooted at target/)
	tar -xJf $(REGLINUX_SCUMMVM_DL_DIR)/$(REGLINUX_SCUMMVM_SOURCE) -C $(TARGET_DIR)/../
endef

$(eval $(generic-package))
