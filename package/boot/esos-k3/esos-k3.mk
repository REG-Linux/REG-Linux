################################################################################
#
# esos-k3 - SpacemiT ESOS (Energy Service OS) firmware for the K3 RT24 cores
#
# ESOS runs on the K3's RT24 real-time coprocessor cores (separate from the
# X100 application cores). It is NOT required to boot Linux on the X100s, but
# the bianbu image layout reserves a 3M partition @4M for esos.itb and U-Boot
# loads it to bring up the RT cores (power-mgmt offload, audio DSP).
#
# Heavyweight build: pulls a vendor bare-metal newlib toolchain at build time
# and runs the ESOS SDK's own build_top.sh (chip rt24). Modeled on bianbu's
# buildroot-ext package/esos. Output esos.itb -> images/esos-k3/.
#
################################################################################

ESOS_K3_VERSION = k3-br-v1.0.y
ESOS_K3_SITE = https://github.com/spacemit-com/esos.git
ESOS_K3_SITE_METHOD = git
ESOS_K3_INSTALL_TARGET = NO
ESOS_K3_INSTALL_STAGING = NO
ESOS_K3_INSTALL_IMAGES = YES

# Bare-metal newlib toolchain for the RT24 (RISC-V RV* embedded) cores.
ESOS_K3_TOOLCHAIN_NAME = spacemit-toolchain-elf-newlib-x86_64-v1.0.9
ESOS_K3_TOOLCHAIN_DIR = $(@D)/tools/toolchain

# Non-interactive config: select chip rt24 and fetch the vendor toolchain.
define ESOS_K3_CONFIGURE_CMDS
	rm -f $(@D)/bsp/spacemit/.config $(@D)/bsp/spacemit/.esos_top.config
	echo "export TOP_TARGET_CHIP=rt24" >> $(@D)/bsp/spacemit/.esos_top.config
	mkdir -p $(ESOS_K3_TOOLCHAIN_DIR)
	if [ ! -d "$(ESOS_K3_TOOLCHAIN_DIR)/$(ESOS_K3_TOOLCHAIN_NAME)" ]; then \
		cd $(ESOS_K3_TOOLCHAIN_DIR) && \
		if [ ! -f "$(ESOS_K3_TOOLCHAIN_NAME).tar.xz" ]; then \
			$(call DOWNLOAD,http://archive.spacemit.com/toolchain/$(ESOS_K3_TOOLCHAIN_NAME).tar.xz) ; \
		fi && \
		tar -xf $(ESOS_K3_TOOLCHAIN_NAME).tar.xz ; \
	fi
	mkdir -p $(@D)/.env/packages
	touch $(@D)/.env/packages/Kconfig
	touch $(@D)/bsp/spacemit/rtconfig.h
endef

define ESOS_K3_BUILD_CMDS
	cd $(@D) && ./build_top.sh
endef

define ESOS_K3_INSTALL_IMAGES_CMDS
	mkdir -p $(BINARIES_DIR)/esos-k3
	test -f $(@D)/bsp/spacemit/esos.itb && \
		cp -f $(@D)/bsp/spacemit/esos.itb $(BINARIES_DIR)/esos-k3/esos.itb || true
endef

$(eval $(generic-package))
