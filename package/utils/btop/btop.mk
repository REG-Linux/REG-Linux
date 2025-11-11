################################################################################
#
# btop
#
################################################################################

BTOP_VERSION = v1.4.5
BTOP_SITE = $(call github,aristocratos,btop,$(BTOP_VERSION))
BTOP_LICENSE = Apache-2.0
BTOP_EXTRA_ARGS = 

ifeq ($(BR2_arm),y)
    BTOP_EXTRA_ARGS += ARCH=aarch32
else ifeq ($(BR2_aarch64),y)
    BTOP_EXTRA_ARGS += ARCH=aarch64
else ifeq ($(BR2_riscv),y)
    BTOP_EXTRA_ARGS += ARCH=riscv64
else ifeq ($(BR2_x86_64),y)
    BTOP_EXTRA_ARGS += ARCH=X86_64
endif

BTOP_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release
BTOP_CONF_OPTS += -DBTOP_LTO=ON

define BTOP_BUILD_CMDS
	$(MAKE) $(TARGET_CONFIGURE_OPTS) $(BTOP_EXTRA_ARGS) -C $(@D)
endef

define BTOP_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/usr/bin
	mkdir -p $(TARGET_DIR)/usr/share/btop
	$(INSTALL) -D $(@D)/bin/btop $(TARGET_DIR)/usr/bin/btop
	cp -prn $(@D)/themes $(TARGET_DIR)/usr/share/btop/
endef

$(eval $(generic-package))
