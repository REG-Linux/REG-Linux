################################################################################
#
# batocera.linux System
#
################################################################################

REGLINUX_SYSTEM_SOURCE=

# stable builds: YY.MM.[0-9]      (after build will be similar to: 24.08.0 2024/08/30 18:53)
# beta builds:   YY.MM-beta-[1-9] (after build will be similar to: 24.08-beta-1 2024/08/30 18:53)
# dev builds:    YY.MM-dev        (after build will be similar to: 24.08-dev-6addb24a75 2024/08/28 18:53)

### Beta release MUST BE marked as "prerelease" ( tag is version = YY.MM-beta-[1-9] )
### Stable release must be marked as "latest" ( tag is version = YY.MM.[0-9] )

REGLINUX_SYSTEM_ID_VERSION = 25.11
REGLINUX_SYSTEM_RELEASE_TYPE=dev
REGLINUX_SYSTEM_VERSION = $(REGLINUX_SYSTEM_ID_VERSION)-$(REGLINUX_SYSTEM_RELEASE_TYPE)
REGLINUX_SYSTEM_DATE_TIME = $(shell date "+%Y/%m/%d %H:%M")
REGLINUX_SYSTEM_DATE = $(shell date "+%Y/%m/%d")
REGLINUX_SYSTEM_DEPENDENCIES = tzdata

ifeq ($(BR2_PACKAGE_SYSTEM_TARGET_BCM2837),y)
	REGLINUX_SYSTEM_ARCH=bcm2837
else ifeq ($(BR2_PACKAGE_SYSTEM_TARGET_RK3399),y)
	REGLINUX_SYSTEM_ARCH=rk3399
else ifeq ($(BR2_PACKAGE_SYSTEM_TARGET_RK3288),y)
	REGLINUX_SYSTEM_ARCH=rk3288
else ifeq ($(BR2_PACKAGE_SYSTEM_TARGET_RK3328),y)
	REGLINUX_SYSTEM_ARCH=rk3328
else ifeq ($(BR2_PACKAGE_SYSTEM_TARGET_RK3568),y)
	REGLINUX_SYSTEM_ARCH=rk3568
else ifeq ($(BR2_PACKAGE_SYSTEM_TARGET_CHA),y)
	REGLINUX_SYSTEM_ARCH=h3
else ifeq ($(BR2_PACKAGE_SYSTEM_TARGET_H3),y)
	REGLINUX_SYSTEM_ARCH=h3
else ifeq ($(BR2_PACKAGE_SYSTEM_TARGET_H5),y)
	REGLINUX_SYSTEM_ARCH=h5
else ifeq ($(BR2_PACKAGE_SYSTEM_TARGET_H6),y)
	REGLINUX_SYSTEM_ARCH=h6
else ifeq ($(BR2_PACKAGE_SYSTEM_TARGET_H616),y)
	REGLINUX_SYSTEM_ARCH=h616
else ifeq ($(BR2_PACKAGE_SYSTEM_TARGET_H700),y)
	REGLINUX_SYSTEM_ARCH=h700
else ifeq ($(BR2_PACKAGE_SYSTEM_TARGET_S812),y)
	REGLINUX_SYSTEM_ARCH=s812
else ifeq ($(BR2_PACKAGE_SYSTEM_TARGET_S922X),y)
	REGLINUX_SYSTEM_ARCH=s922x
else ifeq ($(BR2_PACKAGE_SYSTEM_TARGET_RK3326),y)
	REGLINUX_SYSTEM_ARCH=rk3326
else ifeq ($(BR2_PACKAGE_SYSTEM_TARGET_RK3128),y)
	REGLINUX_SYSTEM_ARCH=rk3128
else ifeq ($(BR2_PACKAGE_SYSTEM_TARGET_XU4),y)
	REGLINUX_SYSTEM_ARCH=odroidxu4
else ifeq ($(BR2_PACKAGE_SYSTEM_TARGET_S905),y)
	REGLINUX_SYSTEM_ARCH=s905
else ifeq ($(BR2_PACKAGE_SYSTEM_TARGET_S905GEN2),y)
	REGLINUX_SYSTEM_ARCH=s905gen2
else ifeq ($(BR2_PACKAGE_SYSTEM_TARGET_S905GEN3),y)
	REGLINUX_SYSTEM_ARCH=s905gen3
else ifeq ($(BR2_PACKAGE_SYSTEM_TARGET_X86),y)
	REGLINUX_SYSTEM_ARCH=x86
else ifeq ($(BR2_PACKAGE_SYSTEM_TARGET_X86_64),y)
	REGLINUX_SYSTEM_ARCH=x86_64
else ifeq ($(BR2_PACKAGE_SYSTEM_TARGET_STEAMDECK),y)
	REGLINUX_SYSTEM_ARCH=steamdeck
else ifeq ($(BR2_PACKAGE_SYSTEM_TARGET_X86_64_V3),y)
	REGLINUX_SYSTEM_ARCH=x86_64_v3
else ifeq ($(BR2_PACKAGE_SYSTEM_TARGET_BCM2836),y)
	REGLINUX_SYSTEM_ARCH=bcm2836
else ifeq ($(BR2_PACKAGE_SYSTEM_TARGET_BCM2835),y)
	REGLINUX_SYSTEM_ARCH=bcm2835
else ifeq ($(BR2_PACKAGE_SYSTEM_TARGET_BCM2711),y)
	REGLINUX_SYSTEM_ARCH=bcm2711
else ifeq ($(BR2_PACKAGE_SYSTEM_TARGET_BCM2712),y)
	REGLINUX_SYSTEM_ARCH=bcm2712
else ifeq ($(BR2_PACKAGE_SYSTEM_TARGET_A3GEN2),y)
	REGLINUX_SYSTEM_ARCH=a3gen2
else ifeq ($(BR2_PACKAGE_SYSTEM_TARGET_SDM845),y)
	REGLINUX_SYSTEM_ARCH=sdm845
else ifeq ($(BR2_PACKAGE_SYSTEM_TARGET_RK3588),y)
	REGLINUX_SYSTEM_ARCH=rk3588
else ifeq ($(BR2_PACKAGE_SYSTEM_TARGET_JH7110)$(BR2_PACKAGE_SYSTEM_TARGET_K1)$(BR2_PACKAGE_SYSTEM_TARGET_TH1520),y)
	REGLINUX_SYSTEM_ARCH=riscv
else ifeq ($(BR2_PACKAGE_SYSTEM_TARGET_SM6115),y)
	REGLINUX_SYSTEM_ARCH=sm6115
else ifeq ($(BR2_PACKAGE_SYSTEM_TARGET_SM8250),y)
	REGLINUX_SYSTEM_ARCH=sm8250
else ifeq ($(BR2_PACKAGE_SYSTEM_TARGET_SM8550),y)
	REGLINUX_SYSTEM_ARCH=sm8550
else
	REGLINUX_SYSTEM_ARCH=unknown
endif

ifneq (,$(findstring dev,$(REGLINUX_SYSTEM_VERSION)))
    REGLINUX_SYSTEM_BUILD_ID = \
	    "$(shell cd $(BR2_EXTERNAL_REGLINUX_PATH) && git rev-parse --short HEAD)"
else
    REGLINUX_SYSTEM_BUILD_ID =
endif

define REGLINUX_SYSTEM_INSTALL_TARGET_CMDS

	# version/arch
	mkdir -p $(TARGET_DIR)/usr/share/reglinux
	echo -n "$(REGLINUX_SYSTEM_ARCH)" > $(TARGET_DIR)/usr/share/reglinux/system.arch
	echo $(REGLINUX_SYSTEM_VERSION)-$(REGLINUX_SYSTEM_BUILD_ID) \
	    $(REGLINUX_SYSTEM_DATE_TIME) > \
		$(TARGET_DIR)/usr/share/reglinux/system.version

	# datainit
        mkdir -p $(TARGET_DIR)/usr/share/reglinux
        rsync -arv $(BR2_EXTERNAL_REGLINUX_PATH)/package/system/reglinux-system/datainit/ $(TARGET_DIR)/usr/share/reglinux/datainit/
	mkdir -p $(TARGET_DIR)/usr/share/reglinux/datainit/system
	cp $(BR2_EXTERNAL_REGLINUX_PATH)/package/system/reglinux-system/system.conf \
	    $(TARGET_DIR)/usr/share/reglinux/datainit/system
	if test "$(BR2_ENABLE_DEBUG)" != "y" ; then sed -i "s/system\.security\.enabled\=0/system\.security\.enabled\=1/" "$(TARGET_DIR)/usr/share/reglinux/datainit/system/system.conf"; fi


	# system-boot.conf
	$(INSTALL) -D -m 0644 \
	    $(BR2_EXTERNAL_REGLINUX_PATH)/package/system/reglinux-system/system-boot.conf \
		$(BINARIES_DIR)/system-boot.conf

	# sysconfigs (default system.conf for boards)
	mkdir -p $(TARGET_DIR)/usr/share/reglinux/sysconfigs
	if test -d \
	    $(BR2_EXTERNAL_REGLINUX_PATH)/package/system/reglinux-system/sysconfigs/${REGLINUX_SYSTEM_ARCH}; \
		then cp -pr \
		$(BR2_EXTERNAL_REGLINUX_PATH)/package/system/reglinux-system/sysconfigs/${REGLINUX_SYSTEM_ARCH}/* \
		$(TARGET_DIR)/usr/share/reglinux/sysconfigs; fi

	# mounts
	mkdir -p $(TARGET_DIR)/boot $(TARGET_DIR)/overlay $(TARGET_DIR)/userdata

	# variables
	mkdir -p $(TARGET_DIR)/etc/profile.d
	cp $(BR2_EXTERNAL_REGLINUX_PATH)/package/system/reglinux-system/xdg.sh \
	    $(TARGET_DIR)/etc/profile.d/xdg.sh
	cp $(BR2_EXTERNAL_REGLINUX_PATH)/package/system/reglinux-system/dbus.sh \
	    $(TARGET_DIR)/etc/profile.d/dbus.sh

	# list of modules that doesnt like suspend
	mkdir -p $(TARGET_DIR)/etc/pm/config.d
	echo 'SUSPEND_MODULES="rtw88_8822ce snd_pci_acp5x"' > $(TARGET_DIR)/etc/pm/config.d/config
endef

$(eval $(generic-package))
