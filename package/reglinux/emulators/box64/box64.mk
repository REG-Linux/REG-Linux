################################################################################
#
# BOX64 emulator
#
################################################################################
# Version.: Release on May 21, 2024
BOX64_VERSION = v0.2.8
BOX64_SITE = https://github.com/ptitseb/box64
BOX64_SITE_METHOD=git
BOX64_LICENSE = GPLv3
BOX64_DEPENDENCIES = host-python3

BOX64_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release -DNOGIT=ON -DUSE_CCACHE=OFF

# AArch64 devices
ifeq ($(BR2_aarch64),y)
ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_BCM2837),y)
BOX64_CONF_OPTS += -DRPI3ARM64=ON
else  ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_BCM2711),y)
BOX64_CONF_OPTS += -DRPI4ARM64=ON
else  ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_BCM2712),y)
BOX64_CONF_OPTS += -DRPI5ARM64=ON
else  ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RK3326),y)
BOX64_CONF_OPTS += -DRK3326=ON
else  ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RK3399),y)
BOX64_CONF_OPTS += -DRK3399=ON
else  ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RK3588),y)
BOX64_CONF_OPTS += -DRK3588=ON
else  ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_S922X)$(BR2_PACKAGE_BATOCERA_TARGET_A3GEN2),y)
BOX64_CONF_OPTS += -DODROIDN2=ON
else  ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_SAPHIRA),y)
BOX64_CONF_OPTS += -DM1=ON
else
BOX64_CONF_OPTS += -DARM64=ON -DSAVE_MEM=ON
endif
# RISC-V 64 devices
else ifeq ($(BR2_RISCV_64),y)
BOX64_CONF_OPTS += -DRV64=ON
endif

$(eval $(cmake-package))
