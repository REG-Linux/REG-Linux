################################################################################
#
# REG-Linux-Rescue - minimal rootfs for rescue/update modes
#
################################################################################

REGLINUX_RESCUE_VERSION = 0.2
REGLINUX_RESCUE_ARCH = ""
ifeq ($(BR2_aarch64),y)
REGLINUX_RESCUE_ARCH = aarch64
else ifeq ($(BR2_riscv),y)
REGLINUX_RESCUE_ARCH = riscv64
else ifeq ($(BR2_x86_64),y)
REGLINUX_RESCUE_ARCH = x86_64
else ifeq ($(BR2_arm),y)
REGLINUX_RESCUE_ARCH = armhf
ifeq ($(BR2_ARM_CPU_ARMV7A),y)
REGLINUX_RESCUE_ARCH = armv7
endif
endif

REGLINUX_RESCUE_SOURCE = REG-linux-rescue-$(REGLINUX_RESCUE_ARCH)
REGLINUX_RESCUE_SITE = https://github.com/REG-Linux/REG-rescue/releases/download/$(REGLINUX_RESCUE_VERSION)

define REGLINUX_RESCUE_EXTRACT_CMDS
	cp $(DL_DIR)/$(REGLINUX_RESCUE_DL_SUBDIR)/$(REGLINUX_RESCUE_SOURCE) $(@D)
endef

define REGLINUX_RESCUE_INSTALL_TARGET_CMDS
	mkdir -p $(BINARIES_DIR)
	cp $(@D)/$(REGLINUX_RESCUE_SOURCE) $(BINARIES_DIR)/rescue
endef

$(eval $(generic-package))
