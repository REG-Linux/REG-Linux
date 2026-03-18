ifeq ($(BR2_PACKAGE_SYSTEM_TARGET_SM8550),y)
# Building the SM8550 EFI payload uses host hexdump to repackage the kernel image.
LINUX_DEPENDENCIES += host-util-linux

# Inject external SM8550 device trees after patching and before kernel build.
define LINUX_SM8550_COPY_DTS
	mkdir -p $(@D)/arch/arm64/boot/dts/qcom
	cp -a $(BR2_EXTERNAL_REGLINUX_PATH)/board/qualcomm/sm8550/dts/. \
		$(@D)/arch/arm64/boot/dts/qcom/
endef
LINUX_PRE_PATCH_HOOKS += LINUX_SM8550_COPY_DTS
endif
