################################################################################
#
# librashader
#
################################################################################

LIBRASHADER_VERSION = librashader-v0.6.2
LIBRASHADER_SITE = $(call github,SnowflakePowered,librashader,$(LIBRASHADER_VERSION))
LIBRASHADER_LICENSE = GPLv3

LIBRASHADER_ARCH = $(BR2_ARCH)
ifeq ($(LIBRASHADER_ARCH),"riscv64")
LIBRASHADER_ARCH = riscv64gc
endif

LIBRASHADER_INSTALL_STAGING = YES

LIBRASHADER_CARGO_BUILD_OPTS += --features stable

define LIBRASHADER_INSTALL_STAGING_CMDS
	cd $(@D)/target/$(LIBRASHADER_ARCH)-unknown-linux-gnu/release/ && \
	cp liblibrashader_capi.so $(STAGING_DIR)/usr/lib/librashader.so.2 && \
	cd $(STAGING_DIR) && ln -sf librashader.so.2 librashader.so && \
	cp $(@D)/pkg/librashader.pc $(STAGING_DIR)/usr/lib/pkgconfig/librashader.pc && \
	mkdir -p $(STAGING_DIR)/usr/include/librashader && \
	cp $(@D)/include/* $(STAGING_DIR)/usr/include/librashader/
endef

define LIBRASHADER_INSTALL_TARGET_CMDS
	cd $(@D)/target/$(LIBRASHADER_ARCH)-unknown-linux-gnu/release/ && \
	cp liblibrashader_capi.so $(TARGET_DIR)/usr/lib/librashader.so.2 && \
	cd $(TARGET_DIR) && ln -sf librashader.so.2 librashader.so
endef

$(eval $(rust-package))
