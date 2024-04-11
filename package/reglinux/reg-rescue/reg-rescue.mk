################################################################################
#
# REG-Rescue - minimal rootfs for rescue/update modes
#
################################################################################

REG_RESCUE_VERSION = 0.1
REG_RESCUE_ARCH = ""
ifeq ($(BR2_aarch64),y)
REG_RESCUE_ARCH = aarch64
else ifeq ($(BR2_riscv),y)
REG_RESCUE_ARCH = riscv64
else ifeq ($(BR2_x86_64),y)
REG_RESCUE_ARCH = x86_64
else ifeq ($(BR2_arm),y)
REG_RESCUE_ARCH = armhf
ifeq ($(BR2_ARM_CPU_ARMV7A),y)
REG_RESCUE_ARCH = armv7
endif
endif

REG_RESCUE_SOURCE = REG-linux-rescue-$(REG_RESCUE_ARCH)
REG_RESCUE_SITE = https://github.com/REG-Linux/REG-rescue/releases/download/$(REG_RESCUE_VERSION)

define REG_RESCUE_EXTRACT_CMDS
	cp $(DL_DIR)/$(REG_RESCUE_DL_SUBDIR)/$(REG_RESCUE_SOURCE) $(@D)
endef

define REG_RESCUE_INSTALL_TARGET_CMDS
	mkdir -p $(BINARIES_DIR)
	cp $(@D)/$(REG_RESCUE_SOURCE) $(BINARIES_DIR)/rescue
endef

$(eval $(generic-package))
