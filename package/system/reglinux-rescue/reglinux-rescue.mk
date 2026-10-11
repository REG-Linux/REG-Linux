################################################################################
#
# REG-Linux-Rescue - minimal rootfs for rescue/update modes
#
################################################################################

REGLINUX_RESCUE_VERSION = 1.4

ifeq ($(BR2_aarch64),y)
REGLINUX_RESCUE_ARCH = aarch64
else ifeq ($(BR2_riscv),y)
REGLINUX_RESCUE_ARCH = riscv64
else ifeq ($(BR2_mipsel),y)
REGLINUX_RESCUE_ARCH = mipsel
else ifeq ($(BR2_x86_64),y)
REGLINUX_RESCUE_ARCH = x86_64
else ifeq ($(BR2_arm),y)
ifeq ($(BR2_ARM_FPU_NEON_VFPV4),y)
REGLINUX_RESCUE_ARCH = armv7
else
REGLINUX_RESCUE_ARCH = armhf
endif
endif

REGLINUX_RESCUE_SOURCE = REG-linux-rescue-$(REGLINUX_RESCUE_ARCH)-$(REGLINUX_RESCUE_VERSION)
REGLINUX_RESCUE_SITE = https://github.com/REG-Linux/REG-rescue/releases/download/$(REGLINUX_RESCUE_VERSION)

REGLINUX_RESCUE_INSTALL_IMAGES = YES

# A bare SquashFS, not an archive: hand it to the build dir as-is.
define REGLINUX_RESCUE_EXTRACT_CMDS
	cp $(REGLINUX_RESCUE_DL_DIR)/$(REGLINUX_RESCUE_SOURCE) $(@D)
endef

define REGLINUX_RESCUE_INSTALL_IMAGES_CMDS
	$(INSTALL) -D -m 0644 $(@D)/$(REGLINUX_RESCUE_SOURCE) $(BINARIES_DIR)/rescue
endef

$(eval $(generic-package))
