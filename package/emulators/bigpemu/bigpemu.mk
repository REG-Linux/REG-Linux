################################################################################
#
# bigpemu
#
################################################################################

BIGPEMU_VERSION = v119
BIGPEMU_SITE = https://www.richwhitehouse.com/jaguar/builds

# x86_64 native builds
ifeq ($(BR2_x86_64),y)
BIGPEMU_ARCH = Linux64
# AArch64 native builds
else ifeq ($(BR2_aarch64),y)
BIGPEMU_ARCH = LinuxARM64
# Fallback on x86_64 for RV64GC (box64 usage)
else
BIGPEMU_ARCH = Linux64
endif

BIGPEMU_SOURCE = BigPEmu_$(BIGPEMU_ARCH)_$(BIGPEMU_VERSION).tar.gz

define BIGPEMU_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/usr/bigpemu
	cp -pr $(@D)/* $(TARGET_DIR)/usr/bigpemu/
	# evmap config
	mkdir -p $(TARGET_DIR)/usr/share/evmapy
	cp -f $(BR2_EXTERNAL_REGLINUX_PATH)/package/emulators/bigpemu/jaguar.bigpemu.keys \
	    $(TARGET_DIR)/usr/share/evmapy
endef

$(eval $(generic-package))
