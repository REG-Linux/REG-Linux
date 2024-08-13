################################################################################
#
# reglinux-qt6
#
################################################################################

ifeq ($(BR2_PACKAGE_REGLINUX_QT6_BUILD_FROM_SOURCE),y)
REGLINUX_QT6_DEPENDENCIES += qt6base qt6declarative qt6multimedia qt6shadertools qt6svg qt6tools qt6wayland qt6websockets
REGLINUX_QT6_INSTALL_STAGING = YES

# Hack needed to retrieve the proper staging name directory when packaging
define REGLINUX_QT6_COMPUTE_STAGING_DIR
	echo "host/$(GNU_TARGET_NAME)/sysroot" > "$(BUILD_DIR)/staging.dir"
endef
REGLINUX_QT6_POST_BUILD_HOOKS = REGLINUX_QT6_COMPUTE_STAGING_DIR

else
REGLINUX_QT6_VERSION = 6.7.2
REGLINUX_QT6_SITE = $(call github,REG-Linux,REG-Qt6,$(REGLINUX_QT6_VERSION))

REGLINUX_QT6_ARCH = unknown
# Cortex A7
#ifeq ($(BR2_cortex_a7),y)
#REGLINUX_QT6_ARCH = bcm2836
# Cortex A9
#else ifeq ($(BR2_cortex_a9),y)
#REGLINUX_QT6_ARCH = s812
# Cortex A15.A7
#else ifeq ($(BR2_cortex_a15_a7),y)
#REGLINUX_QT6_ARCH = odroidxu4
# Cortex A17
#else
ifeq ($(BR2_cortex_a17),y)
REGLINUX_QT6_ARCH = rk3288
# Cortex A53
else ifeq ($(BR2_cortex_a53),y)
REGLINUX_QT6_ARCH = h5
# Cortex A35 + MALI
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_S9GEN4),y)
REGLINUX_QT6_ARCH = s9gen4
# A311D2 (MALI)
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_A3GEN2),y)
REGLINUX_QT6_ARCH = a3gen2
# Cortex A35
else ifeq ($(BR2_cortex_a35),y)
REGLINUX_QT6_ARCH = rk3326
# Cortex A55
else ifeq ($(BR2_cortex_a55),y)
REGLINUX_QT6_ARCH = s905gen3
# Cortex A72
else ifeq ($(BR2_cortex_a72),y)
REGLINUX_QT6_ARCH = bcm2711
# Cortex A72.A53
else ifeq ($(BR2_cortex_a72_a53),y)
REGLINUX_QT6_ARCH = rk3399
# Cortex A73.A53
else ifeq ($(BR2_cortex_a73_a53),y)
REGLINUX_QT6_ARCH = s922x
# Cortex A76
else ifeq ($(BR2_cortex_a76),y)
REGLINUX_QT6_ARCH = bcm2712
# Cortex A76.A55
else ifeq ($(BR2_cortex_a76_a55),y)
REGLINUX_QT6_ARCH = rk3588
# Unknown AArch64 saphira CPU
else ifeq ($(BR2_saphira),y)
REGLINUX_QT6_ARCH = saphira
# RISC-V 64 (rv64gc, aka imafd)
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_JH7110),y)
REGLINUX_QT6_ARCH = jh7110
# RISC-V 64 with vector extensions (aka imafdv)
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_K1),y)
REGLINUX_QT6_ARCH = k1
# X86_64-v3 subarchitecture
else ifeq ($(BR2_x86_64_v3),y)
REGLINUX_QT6_ARCH = x86_64_v3
# X86_64 architecture
else ifeq ($(BR2_x86_64),y)
REGLINUX_QT6_ARCH = x86_64
endif

# Compute the archive source file name
REGLINUX_QT6_SOURCE = reglinux-qt6-$(REGLINUX_QT6_VERSION)-$(REGLINUX_QT6_ARCH).tar.gz

define REGLINUX_QT6_DOWNLOAD_ARCHIVE
	echo "Downloading https://github.com/REG-Linux/REG-Qt6/releases/download/$(REGLINUX_QT6_VERSION)/$(REGLINUX_QT6_SOURCE)"
	cd $(@D) && wget https://github.com/REG-Linux/REG-Qt6/releases/download/$(REGLINUX_QT6_VERSION)/$(REGLINUX_QT6_SOURCE)
endef

REGLINUX_QT6_POST_BUILD_HOOKS = REGLINUX_QT6_DOWNLOAD_ARCHIVE

define REGLINUX_QT6_INSTALL_TARGET_CMDS
	# copy the prebuilt stuff to rootfs
	tar xzvf $(@D)/$(REGLINUX_QT6_SOURCE) -C $(HOST_DIR)/../

	# delete the archive from this directory
	rm $(@D)/$(REGLINUX_QT6_SOURCE)
endef

endif

$(eval $(generic-package))
