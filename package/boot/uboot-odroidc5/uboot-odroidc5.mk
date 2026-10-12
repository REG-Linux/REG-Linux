################################################################################
#
# uboot files for ODROID C5
#
################################################################################

# Prebuilt signed bootloader from Hardkernel. There is no public source for the
# Amlogic S7D BSP U-Boot, so the blob is vendored here and written at offset 512
# by genimage.cfg (matching Hardkernel's own "dd bs=512 seek=1").
#
# Refresh it from Hardkernel's package repository:
#   http://ppa.linuxfactory.or.kr/pool/main/u/u-boot-odroidc5/
#   dpkg-deb -x <deb> x && cp x/usr/lib/u-boot/odroidc5/u-boot.bin u-boot.bin.signed
#
# The blob carries its build stamp as an ASCII tag, so staleness is checkable:
#   strings -a u-boot.bin.signed | grep S7D-s905x5m   ->  S7D-s905x5m-26060818BBST
# Current blob: 26060818 (2026-06-08), byte-identical to the U-Boot shipped in
# Hardkernel's ubuntu-26.04-weston-odroidc5-20260616 image.
UBOOT_ODROIDC5_VERSION = 2025.01
UBOOT_ODROIDC5_SOURCE =

define UBOOT_ODROIDC5_BUILD_CMDS
endef

define UBOOT_ODROIDC5_INSTALL_TARGET_CMDS
	mkdir -p $(BINARIES_DIR)/uboot-odroidc5/
	cp $(BR2_EXTERNAL_REGLINUX_PATH)/package/boot/uboot-odroidc5/u-boot.bin.signed $(BINARIES_DIR)/uboot-odroidc5/u-boot.bin.signed
endef

$(eval $(generic-package))
