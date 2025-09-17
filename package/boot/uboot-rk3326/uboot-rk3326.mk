################################################################################
#
# uboot files for RK3326
#
################################################################################

UBOOT_RK3326_VERSION = 611716febddb824a7203d0d3b5d399608a54ccf6
UBOOT_RK3326_SITE = https://github.com/ROCKNIX/hardkernel-uboot.git
UBOOT_RK3326_SITE_METHOD=git

#UBOOT_RK3326_ARCH = arm
UBOOT_RK3326_ARCH = aarch64

# CONFIG_SYS_TEXT_BASE=0x00200000
UBOOT_RK3326_LOAD_ADDR = 0x00200000
#UBOOT_RK3326_TRUST_INI = ./RKTRUST/RK3326TRUST.ini
#UBOOT_RK3326_BL31_ELF = bin/rk33/rk3326_bl31_v1.34.elf
define UBOOT_RK3326_BUILD_CMDS
	# Build U-Boot
	cd $(@D) && ARCH=$(UBOOT_RK3326_ARCH) $(MAKE) mrproper
	cd $(@D) && ARCH=$(UBOOT_RK3326_ARCH) $(MAKE) odroidgoa_defconfig
	cd $(@D) && PATH="$(HOST_DIR)/bin:$$PATH" \
	CROSS_COMPILE="aarch64-buildroot-linux-musl-" \
	ARCH=$(UBOOT_RK3326_ARCH) \
	$(MAKE)
	# Clone rkbin
	cd $(@D) && git clone --depth 1 https://github.com/rockchip-linux/rkbin
	# Pack idbloader.img
	cd $(@D) && ./tools/mkimage -n px30 -T rksd -d ./rkbin/bin/rk33/rk3326_ddr_333MHz_v2.11.bin ./sd_fuse/idbloader.img
        cd $(@D) && cat rkbin/bin/rk33/rk3326_miniloader_v1.40.bin >> ./sd_fuse/idbloader.img
        # Pack uboot.img
	cd $(@D) && ./rkbin/tools/loaderimage --pack --uboot ./u-boot-dtb.bin ./sd_fuse/uboot.img $(UBOOT_RK3326_LOAD_ADDR)
        # Pack trust.img
	cp $(BR2_EXTERNAL_REGLINUX_PATH)/package/boot/uboot-rk3326/trust.ini $(@D)/trust.ini
	cd $(@D)/rkbin/ && ./tools/trust_merger --verbose --replace tools/rk_tools/ ./ $(@D)/trust.ini
	# Copy trust.img
	cd $(@D) && cp ./rkbin/trust.img ./sd_fuse/trust.img
endef

define UBOOT_RK3326_INSTALL_TARGET_CMDS
	cp $(@D)/sd_fuse/idbloader.img $(BINARIES_DIR)/idbloader.img
	cp $(@D)/sd_fuse/uboot.img     $(BINARIES_DIR)/uboot.img
	cp $(@D)/sd_fuse/trust.img     $(BINARIES_DIR)/trust.img
endef

$(eval $(generic-package))
