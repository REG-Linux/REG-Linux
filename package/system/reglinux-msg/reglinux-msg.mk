################################################################################
#
# regmsg
#
################################################################################

# branch: main
REGLINUX_MSG_VERSION = 532138354e3ee871838954a016342892d51dc7fb

ifeq ($(BR2_PACKAGE_REGLINUX_MSG_BUILD_FROM_SOURCE),y)

REGLINUX_MSG_TOKEN = $(shell cat /build/gh_token)
REGLINUX_MSG_SITE = https://$(REGLINUX_MSG_TOKEN)@github.com/REG-Linux/regmsg
REGLINUX_MSG_SITE_METHOD = git
REGLINUX_MSG_LICENSE = MIT
REGLINUX_MSG_LICENSE_FILES = LICENSE
REGLINUX_MSG_DEPENDENCIES += libdrm

RUSTC_TARGET_PROFILE = $(if $(BR2_ENABLE_DEBUG),,release)
REGLINUX_MSG_LOCATION = target/$(RUSTC_TARGET_NAME)/$(RUSTC_TARGET_PROFILE)
REGLINUX_MSG_CARGO_BUILD_OPTS += --features integrity

define REGLINUX_MSG_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/$(REGLINUX_MSG_LOCATION)/regmsg			$(TARGET_DIR)/usr/bin/
	$(INSTALL) -D $(@D)/$(REGLINUX_MSG_LOCATION)/regmsgd			$(TARGET_DIR)/usr/bin/
	$(INSTALL) -D $(@D)/$(REGLINUX_MSG_LOCATION)/regmsg_shell		$(TARGET_DIR)/usr/bin/
	$(INSTALL) -D $(@D)/target/$(RUSTC_TARGET_PROFILE)/libdrmhook.so	$(TARGET_DIR)/usr/lib/
	$(INSTALL) -D $(@D)/target/$(RUSTC_TARGET_PROFILE)/S06regmsgd		$(TARGET_DIR)/etc/init.d/
endef

$(eval $(cargo-package))

else
# Download pre compiled files

REGLINUX_MSG_CPU = unknown
ifeq ($(BR2_arm1176jzf_s),y)
	REGLINUX_MSG_CPU = arm1176jzf_s
else ifeq ($(BR2_cortex_a7),y)
	REGLINUX_MSG_CPU = cortex_a7
else ifeq ($(BR2_cortex_a9),y)
	REGLINUX_MSG_CPU = cortex_a9
else ifeq ($(BR2_cortex_a15_a7),y)
	REGLINUX_MSG_CPU = cortex_a15_a7
else ifeq ($(BR2_cortex_a17),y)
	REGLINUX_MSG_CPU = cortex_a17
else ifeq ($(BR2_cortex_a35),y)
	REGLINUX_MSG_CPU = cortex_a35
else ifeq ($(BR2_cortex_a53),y)
	REGLINUX_MSG_CPU = cortex_a53
else ifeq ($(BR2_jz4770),y)
	REGLINUX_MSG_CPU = jz4770
else ifeq ($(BR2_cortex_a55),y)
	REGLINUX_MSG_CPU = cortex_a55
else ifeq ($(BR2_cortex_a72),y)
	REGLINUX_MSG_CPU = cortex_a72
else ifeq ($(BR2_cortex_a72_a53),y)
	REGLINUX_MSG_CPU = cortex_a72_a53
else ifeq ($(BR2_cortex_a73_a53),y)
	REGLINUX_MSG_CPU = cortex_a73_a53
else ifeq ($(BR2_cortex_a75_a55),y)
	REGLINUX_MSG_CPU = cortex_a75_a55
else ifeq ($(BR2_cortex_a76),y)
	REGLINUX_MSG_CPU = cortex_a76
else ifeq ($(BR2_cortex_a76_a55),y)
	REGLINUX_MSG_CPU = cortex_a76_a55
else ifeq ($(BR2_ARM_CPU_ARMV9A),y) # TODO
	REGLINUX_MSG_CPU = cortex_a76_a55
else ifeq ($(BR2_riscv),y)
	REGLINUX_MSG_CPU = riscv
else ifeq ($(BR2_saphira),y)
	REGLINUX_MSG_CPU = saphira
else ifeq ($(BR2_x86_x86_64_v3),y)
	REGLINUX_MSG_CPU = x86_64_v3
else ifeq ($(BR2_x86_64),y)
	REGLINUX_MSG_CPU = x86_64
endif

REGLINUX_MSG_SHORT_VERSION := $(shell printf '%s' "$(REGLINUX_MSG_VERSION)" | cut -c1-7)
REGLINUX_MSG_SITE = https://github.com/REG-Linux/regmsg-binaries/releases/download/$(REGLINUX_MSG_SHORT_VERSION)
REGLINUX_MSG_SOURCE = reglinux-msg-$(REGLINUX_MSG_SHORT_VERSION)-$(REGLINUX_MSG_CPU).tar.xz

define REGLINUX_MSG_INSTALL_TARGET_CMDS
	# extract target folder
	tar -C $(TARGET_DIR)/../ -xvf $(DL_DIR)/$(REGLINUX_MSG_DL_SUBDIR)/$(REGLINUX_MSG_SOURCE) target
endef

$(eval $(generic-package))
endif
