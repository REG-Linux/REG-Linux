################################################################################
#
# TH1520 vendor firmware - AON, Audio DSP, and STR
#
# These proprietary T-Head firmware files are loaded by the vendor U-Boot
# before the kernel boots:
#   - light_aon_fpga.bin: E902 Always-On subsystem (poweroff/reboot)
#   - light_c906_audio.bin: C906 audio DSP
#   - str.bin: Suspend-to-RAM support
#
# Source: RevyOS boot images (https://github.com/revyos/mkimg-th1520)
#
################################################################################

TH1520_VENDOR_FIRMWARE_VERSION = 1.0
TH1520_VENDOR_FIRMWARE_SOURCE =

define TH1520_VENDOR_FIRMWARE_INSTALL_TARGET_CMDS
	mkdir -p $(BINARIES_DIR)/th1520-vendor-firmware
	cp $(BR2_EXTERNAL_REGLINUX_PATH)/package/boot/th1520-vendor-firmware/light_aon_fpga.bin    $(BINARIES_DIR)/th1520-vendor-firmware/
	cp $(BR2_EXTERNAL_REGLINUX_PATH)/package/boot/th1520-vendor-firmware/light_c906_audio.bin  $(BINARIES_DIR)/th1520-vendor-firmware/
	cp $(BR2_EXTERNAL_REGLINUX_PATH)/package/boot/th1520-vendor-firmware/str.bin               $(BINARIES_DIR)/th1520-vendor-firmware/
endef

$(eval $(generic-package))
