################################################################################
#
# switch-atf
#
# ARM Trusted Firmware (BL31) for the Nintendo Switch Tegra T210 SoC
# Based on Lakka-LibreELEC's switch-atf package
#
################################################################################

SWITCH_ATF_VERSION = 8902c539ce83b15637c5f47fc8aff5d14d95b992
SWITCH_ATF_SITE = https://gitlab.com/switchroot/bootstack/switch-atf.git
SWITCH_ATF_SITE_METHOD = git
SWITCH_ATF_GIT_SUBMODULES = YES
SWITCH_ATF_LICENSE = BSD-3-Clause
SWITCH_ATF_LICENSE_FILES = license.rst
SWITCH_ATF_DEPENDENCIES = host-dtc

define SWITCH_ATF_BUILD_CMDS
	$(TARGET_MAKE_ENV) $(MAKE) -C $(@D) \
		CROSS_COMPILE="$(TARGET_CROSS)" \
		LDFLAGS="--emit-relocs" \
		CFLAGS="-fno-pic -fno-stack-protector -Wno-deprecated-declarations -Wno-unused-function" \
		bl31 \
		PLAT=tegra \
		TARGET_SOC=t210 \
		TZDRAM_BASE=0xFFF00000 \
		RESET_TO_BL31=1 \
		COLD_BOOT_SINGLE_CPU=1 \
		PROGRAMMABLE_RESET_ADDRESS=1 \
		ENABLE_STACK_PROTECTOR=none \
		SDEI_SUPPORT=0 \
		CRASH_REPORTING=1 \
		ENABLE_ASSERTIONS=1 \
		LOG_LEVEL=0 \
		PLAT_LOG_LEVEL_ASSERT=0
endef

define SWITCH_ATF_INSTALL_TARGET_CMDS
	$(INSTALL) -D -m 0644 $(@D)/build/tegra/t210/release/bl31.bin \
		$(TARGET_DIR)/usr/share/bootloader/boot/bl31.bin
endef

$(eval $(generic-package))
