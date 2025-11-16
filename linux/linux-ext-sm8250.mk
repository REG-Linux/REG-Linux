ifeq ($(BR2_PACKAGE_SYSTEM_TARGET_SM8250),y)
	# Building the SM8250 EFI payload uses host hexdump to repackage the kernel image.
	LINUX_DEPENDENCIES += host-util-linux
endif
