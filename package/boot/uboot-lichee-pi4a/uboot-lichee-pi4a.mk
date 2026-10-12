################################################################################
#
# uboot for Lichee Pi 4A / TH1520 - built from mainline
#
################################################################################

UBOOT_LICHEE_PI4A_VERSION = v2026.01
UBOOT_LICHEE_PI4A_SITE = https://github.com/u-boot/u-boot.git
UBOOT_LICHEE_PI4A_SITE_METHOD = git
UBOOT_LICHEE_PI4A_GIT_SUBMODULES = YES
UBOOT_LICHEE_PI4A_INSTALL_TARGET = NO
UBOOT_LICHEE_PI4A_INSTALL_STAGING = NO
UBOOT_LICHEE_PI4A_INSTALL_IMAGES = YES
UBOOT_LICHEE_PI4A_DEPENDENCIES = opensbi th1520-ddr-firmware host-flex host-bison host-python3 host-python-setuptools host-python-pylibfdt host-uboot-tools

UBOOT_LICHEE_PI4A_MAKE_OPTS = \
	CROSS_COMPILE=$(TARGET_CROSS) \
	OPENSBI=$(BINARIES_DIR)/fw_dynamic.bin \
	BINMAN_INDIRS=$(BINARIES_DIR)

define UBOOT_LICHEE_PI4A_BUILD_CMDS
	$(TARGET_MAKE_ENV) $(MAKE) -C $(@D) $(UBOOT_LICHEE_PI4A_MAKE_OPTS) th1520_lpi4a_defconfig
	$(TARGET_MAKE_ENV) $(MAKE) -C $(@D) $(UBOOT_LICHEE_PI4A_MAKE_OPTS)
endef

define UBOOT_LICHEE_PI4A_INSTALL_IMAGES_CMDS
	mkdir -p $(BINARIES_DIR)/uboot-lichee-pi4a
	cp $(@D)/u-boot-with-spl.bin $(BINARIES_DIR)/uboot-lichee-pi4a/u-boot-with-spl.bin
endef

$(eval $(generic-package))
