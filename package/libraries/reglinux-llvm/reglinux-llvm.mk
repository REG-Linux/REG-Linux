################################################################################
#
# reglinux-llvm
#
################################################################################

# 19.1.7
REGLINUX_LLVM_VERSION = $(LLVM_PROJECT_VERSION)
REGLINUX_LLVM_SITE = $(call github,REG-Linux,REG-llvm-binaries,$(REGLINUX_LLVM_VERSION))

REGLINUX_LLVM_DEPENDENCIES = host-python3

REGLINUX_LLVM_ARCH = unknown
ifeq ($(BR2_arm),y)
ifeq ($(BR2_arm1176jzf_s),y)
    # bcm2835
    REGLINUX_LLVM_ARCH = armhf
else
    # h3
    REGLINUX_LLVM_ARCH = armv7
endif
else ifeq ($(BR2_aarch64),y)
ifeq ($(BR2_saphira),y)
    # Asahi Linux
    REGLINUX_LLVM_ARCH = asahi
else
    # h5, Cortex A53
    REGLINUX_LLVM_ARCH = aarch64
endif
else ifeq ($(BR2_RISCV_64),y)
# jh7110, RISC-V 64 (rv64gc, aka imafd)
REGLINUX_LLVM_ARCH = riscv64
else ifeq ($(BR2_x86_64),y)
# X86_64 architecture
REGLINUX_LLVM_ARCH = x86_64
endif

# Compute the archive source file name
REGLINUX_LLVM_SOURCE = reglinux-llvm-$(REGLINUX_LLVM_VERSION)-$(REGLINUX_LLVM_ARCH).tar.xz

define REGLINUX_LLVM_DOWNLOAD_ARCHIVE
	echo "Downloading https://github.com/REG-Linux/REG-llvm-binaries/releases/download/$(REGLINUX_LLVM_VERSION)/$(REGLINUX_LLVM_SOURCE)"
	cd $(@D) && wget https://github.com/REG-Linux/REG-llvm-binaries/releases/download/$(REGLINUX_LLVM_VERSION)/$(REGLINUX_LLVM_SOURCE)
endef

REGLINUX_LLVM_POST_BUILD_HOOKS = REGLINUX_LLVM_DOWNLOAD_ARCHIVE

define REGLINUX_LLVM_INSTALL_TARGET_CMDS
	# copy the prebuilt stuff to rootfs
	tar xvf $(@D)/$(REGLINUX_LLVM_SOURCE) -C $(HOST_DIR)/../

	# delete the archive from this directory
	rm $(@D)/$(REGLINUX_LLVM_SOURCE)
endef

endif

$(eval $(generic-package))
