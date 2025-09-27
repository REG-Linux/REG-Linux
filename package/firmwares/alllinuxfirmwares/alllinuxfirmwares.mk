################################################################################
#
# alllinuxfirmwares
#
################################################################################

ALLLINUXFIRMWARES_VERSION = 20250917
ALLLINUXFIRMWARES_SITE = https://gitlab.com/kernel-firmware/linux-firmware
ALLLINUXFIRMWARES_SITE_METHOD = git

# exclude some dirs not required on REG
ALLLINUXFIRMWARES_REMOVE_FILES = $(@D)/liquidio $(@D)/netronome $(@D)/mellanox $(@D)/dpaa2 $(@D)/bnx2x $(@D)/cxgb4 $(@D)/mrvl/prestera

ifneq ($(BR2_x86_64),y)
    ALLLINUXFIRMWARES_REMOVE_FILES += $(@D)/intel $(@D)/i915 $(@D)/nvidia $(@D)/radeon $(@D)/qat_* $(@D)/ql2* $(@D)/iwlwifi* $(@D)/qed $(@D)/amd* $(@D)/xe/*
else
    ALLLINUXFIRMWARES_REMOVE_FILES += $(@D)/amlogic $(@D)/meson $(@D)/arm $(@D)/rockchip $(@D)/powervr $(@D)/imx $(@D)/nxp $(@D)/qed
endif

ifeq ($(BR2_PACKAGE_SYSTEM_TARGET_CHA)$(BR2_PACKAGE_SYSTEM_TARGET_MINI),y)
    ALLLINUXFIRMWARES_REMOVE_FILES += $(@D)/ath10k $(@D)/ath11k $(@D)/ath12k $(@D)/mediatek $(@D)/mrvl $(@D)/ti-connectivity $(@D)/rtw89 $(@D)/cypress
    ALLLINUXFIRMWARES_REMOVE_FILES += $(@D)/brcm $(@D)/cirrus $(@D)/qca $(@D)/ueagle-atm $(@D)/libertas $(@D)/phanfw.bin $(@D)/rsi $(@D)/nxp
    ALLLINUXFIRMWARES_REMOVE_FILES += $(@D)/ti $(@D)/b43 $(@D)/amlogic $(@D)/carl9170fw $(@D)/cnm
    ALLLINUXFIRMWARES_REMOVE_FILES += $(@D)/s5p-* $(@D)/myri*
endif

ifeq ($(BR2_PACKAGE_SYSTEM_TARGET_H700)$(BR2_PACKAGE_SYSTEM_TARGET_RK3326),y)
    ALLLINUXFIRMWARES_REMOVE_FILES += $(@D)/ath10k $(@D)/ath11k $(@D)/ath12k $(@D)/mediatek $(@D)/mrvl $(@D)/ti-connectivity $(@D)/rtw89 $(@D)/cypress
    ALLLINUXFIRMWARES_REMOVE_FILES += $(@D)/cirrus $(@D)/qca $(@D)/ueagle-atm $(@D)/libertas $(@D)/phanfw.bin $(@D)/rsi $(@D)/nxp
    ALLLINUXFIRMWARES_REMOVE_FILES += $(@D)/ti $(@D)/amlogic $(@D)/carl9170fw $(@D)/cnm $(@D)/s5p-* $(@D)/myri*
endif

ifeq ($(BR2_PACKAGE_BRCMFMAC_SDIO_FIRMWARE_RPI),y)
    ALLLINUXFIRMWARES_REMOVE_FILES += $(@D)/brcm
endif

# Remove qualcomm firmware if not building for snapdragon targets
ifneq ($(BR2_PACKAGE_SYSTEM_TARGET_ODIN)$(BR2_PACKAGE_SYSTEM_TARGET_SM6115)$(BR2_PACKAGE_SYSTEM_TARGET_SM8250)$(BR2_PACKAGE_SYSTEM_TARGET_SM8550),y)
    ALLLINUXFIRMWARES_REMOVE_FILES += $(@D)/qcom
endif

ifeq ($(BR2_PACKAGE_SYSTEM_TARGET_SM8250),y)

# List of firmware files to keep, read from a manifest
ALLLINUXFIRMWARES_FILELIST = $(sort $(shell sed -e 's/#.*//' -e '/^$$/d' $(BR2_EXTERNAL_REGLINUX_PATH)/board/qualcomm/sm8250/kernel-firmware.txt))

define ALLLINUXFIRMWARES_INSTALL_TARGET_CMDS
	# Create target firmware dir
	mkdir -p $(TARGET_DIR)/lib/firmware

	#for f in $(ALLLINUXFIRMWARES_FILELIST); do \
	#	$(INSTALL) -Dm0644 $(@D)/$$f $(TARGET_DIR)/lib/firmware/$$f || exit 1; \
	#done

	# Copy only the requested files and create required folders before
	for f in $(ALLLINUXFIRMWARES_FILELIST); do \
		for src in $(@D)/$$f; do \
			if [ -e "$$src" ]; then \
				dest=$(TARGET_DIR)/lib/firmware/$${src#$(@D)/}; \
				mkdir -p $$(dirname $$dest); \
				install -m0644 $$src $$dest; \
			fi; \
		done; \
	done

    # Some firmware are distributed as a symlink, for drivers to load them using a
    # defined name other than the real one. Since 9cfefbd7fbda ("Remove duplicate
    # symlinks") those symlink aren't distributed in linux-firmware but are created
    # automatically by its copy-firmware.sh script during the installation, which
    # parses the WHENCE file where symlinks are described. We follow the same logic
    # here, adding symlink only for firmwares installed in the target directory.
    cd $(TARGET_DIR)/lib/firmware ; \
    sed -r -e '/^Link: (.+) -> (.+)$$/!d; s//\1 \2/' $(@D)/WHENCE | \
	while read f d; do \
		if test -f $$(readlink -m $$(dirname "$$f")/$$d); then \
            if test -f $(TARGET_DIR)/lib/firmware/$$(dirname "$$f")/$$d; then \
                ln -sf $$d "$$f" || exit 1; \
            fi \
		fi ; \
	done
endef
else

define ALLLINUXFIRMWARES_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/lib/firmware

    # exclude some dirs not required on REG
    rm -rf $(ALLLINUXFIRMWARES_REMOVE_FILES)

    # -n is mandatory while some other packages provides firmwares too
    # this is not ideal, but i don't know how to tell to buildroot to install this package first (and not worry about all packages installing firmwares)
    cp --remove-destination -prn $(@D)/* $(TARGET_DIR)/lib/firmware/

    # Some firmware are distributed as a symlink, for drivers to load them using a
    # defined name other than the real one. Since 9cfefbd7fbda ("Remove duplicate
    # symlinks") those symlink aren't distributed in linux-firmware but are created
    # automatically by its copy-firmware.sh script during the installation, which
    # parses the WHENCE file where symlinks are described. We follow the same logic
    # here, adding symlink only for firmwares installed in the target directory.
    cd $(TARGET_DIR)/lib/firmware ; \
    sed -r -e '/^Link: (.+) -> (.+)$$/!d; s//\1 \2/' $(@D)/WHENCE | \
	while read f d; do \
		if test -f $$(readlink -m $$(dirname "$$f")/$$d); then \
            if test -f $(TARGET_DIR)/lib/firmware/$$(dirname "$$f")/$$d; then \
                ln -sf $$d "$$f" || exit 1; \
            fi \
		fi ; \
	done
endef

define ALLLINUXFIRMWARES_LINK_QCA_WIFI_BT
    # wifi
    mkdir -p $(TARGET_DIR)/lib/firmware/ath11k/WCN6855/hw2.1
    mkdir -p $(TARGET_DIR)/lib/firmware/ath11k/QCA2066
    cp -rf $(BR2_EXTERNAL_REGLINUX_PATH)/package/firmwares/alllinuxfirmwares/hw2.1/* \
	    $(TARGET_DIR)/lib/firmware/ath11k/WCN6855/hw2.1
    cp -rf $(BR2_EXTERNAL_REGLINUX_PATH)/package/firmwares/alllinuxfirmwares/QCA206X/* \
	    $(TARGET_DIR)/lib/firmware/ath11k/QCA2066
    # bluetooth
    cp -rf $(BR2_EXTERNAL_REGLINUX_PATH)/package/firmwares/alllinuxfirmwares/qca/* \
	    $(TARGET_DIR)/lib/firmware/qca
endef

# Copy Qualcomm firmware for Steam Deck OLED
ifeq ($(BR2_x86_64),y)
    ALLLINUXFIRMWARES_POST_INSTALL_TARGET_HOOKS = ALLLINUXFIRMWARES_LINK_QCA_WIFI_BT
endif

# symlink BT firmware for RK3588 kernel
define ALLLINUXFIRMWARES_LINK_RTL_BT
    ln -sf /lib/firmware/rtl_bt/rtl8852bu_fw.bin \
        $(TARGET_DIR)/lib/firmware/rtl8852bu_fw
    ln -sf /lib/firmware/rtl_bt/rtl8852bu_config.bin \
        $(TARGET_DIR)/lib/firmware/rtl8852bu_config
endef

ifeq ($(BR2_PACKAGE_SYSTEM_TARGET_RK3588),y)
    ALLLINUXFIRMWARES_POST_INSTALL_TARGET_HOOKS = ALLLINUXFIRMWARES_LINK_RTL_BT
endif

endif

$(eval $(generic-package))
