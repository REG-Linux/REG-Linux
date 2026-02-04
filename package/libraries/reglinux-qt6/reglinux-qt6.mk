################################################################################
#
# reglinux-qt6
#
################################################################################

ifeq ($(BR2_PACKAGE_REGLINUX_QT6_BUILD_FROM_SOURCE),y)
REGLINUX_QT6_DEPENDENCIES += qt6base qt6declarative qt6multimedia qt6shadertools qt6svg qt6tools qt6wayland qt6websockets
REGLINUX_QT6_INSTALL_STAGING = YES

# Hack needed to retrieve the proper staging name directory when packaging
define REGLINUX_QT6_COMPUTE_STAGING_DIR
	echo "host/$(GNU_TARGET_NAME)/sysroot" > "$(BUILD_DIR)/staging.dir"
endef
REGLINUX_QT6_POST_BUILD_HOOKS = REGLINUX_QT6_COMPUTE_STAGING_DIR

else
# Prebuilt Qt6 package

REGLINUX_QT6_CPU = unknown
ifeq ($(BR2_arm1176jzf_s),y)
	REGLINUX_QT6_CPU = arm1176jzf_s
else ifeq ($(BR2_cortex_a7),y)
	REGLINUX_QT6_CPU = cortex_a7
else ifeq ($(BR2_cortex_a9),y)
	REGLINUX_QT6_CPU = cortex_a9
else ifeq ($(BR2_cortex_a15_a7),y)
	REGLINUX_QT6_CPU = cortex_a15_a7
else ifeq ($(BR2_cortex_a17),y)
	REGLINUX_QT6_CPU = cortex_a17
else ifeq ($(BR2_cortex_a35),y)
	REGLINUX_QT6_CPU = cortex_a35
else ifeq ($(BR2_cortex_a53),y)
	REGLINUX_QT6_CPU = cortex_a53
else ifeq ($(BR2_jz4770),y)
	REGLINUX_QT6_CPU = jz4770
else ifeq ($(BR2_cortex_a55),y)
	REGLINUX_QT6_CPU = cortex_a55
else ifeq ($(BR2_cortex_a72),y)
	REGLINUX_QT6_CPU = cortex_a72
else ifeq ($(BR2_cortex_a72_a53),y)
	REGLINUX_QT6_CPU = cortex_a72_a53
else ifeq ($(BR2_cortex_a73_a53),y)
	REGLINUX_QT6_CPU = cortex_a73_a53
else ifeq ($(BR2_cortex_a75_a55),y)
	REGLINUX_QT6_CPU = cortex_a75_a55
else ifeq ($(BR2_cortex_a76),y)
	REGLINUX_QT6_CPU = cortex_a76
else ifeq ($(BR2_cortex_a76_a55),y)
	REGLINUX_QT6_CPU = cortex_a76_a55
else ifeq ($(BR2_ARM_CPU_ARMV9A),y)
	REGLINUX_QT6_CPU = cortex_a76_a55
else ifeq ($(BR2_riscv),y)
	REGLINUX_QT6_CPU = riscv
else ifeq ($(BR2_saphira),y)
	REGLINUX_QT6_CPU = saphira
else ifeq ($(BR2_x86_x86_64_v3),y)
	REGLINUX_QT6_CPU = x86_64_v3
else ifeq ($(BR2_x86_64),y)
	REGLINUX_QT6_CPU = x86_64
endif

REGLINUX_QT6_VERSION = 6.10.1
REGLINUX_QT6_SITE = https://github.com/REG-Linux/REG-Qt6-binaries/releases/download/$(REGLINUX_QT6_VERSION)
REGLINUX_QT6_SOURCE = reglinux-qt6-$(REGLINUX_QT6_VERSION)-$(REGLINUX_QT6_CPU).tar.xz

REGLINUX_QT6_DEPENDENCIES = host-double-conversion double-conversion host-libb2 libb2 host-pcre2 pcre2 host-zlib zlib icu
REGLINUX_QT6_DEPENDENCIES += fontconfig libglib2 libpng freetype dbus

ifeq ($(BR2_PACKAGE_HAS_LIBGL),y)
REGLINUX_QT6_DEPENDENCIES += libgl
endif

ifeq ($(BR2_PACKAGE_HAS_LIBGLES),y)
REGLINUX_QT6_DEPENDENCIES += libgles
endif

ifeq ($(BR2_PACKAGE_REGLINUX_XWAYLAND),y)
REGLINUX_QT6_DEPENDENCIES += libxkbcommon xcb-util-cursor xcb-util-keysyms
endif

define REGLINUX_QT6_INSTALL_TARGET_CMDS
	# extract target folder
	tar xvf $(DL_DIR)/$(REGLINUX_QT6_DL_SUBDIR)/$(REGLINUX_QT6_SOURCE) -C $(HOST_DIR)/../
endef

endif

$(eval $(generic-package))
