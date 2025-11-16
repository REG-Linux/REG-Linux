ifeq ($(BR2_PACKAGE_SYSTEM_TARGET_SM8250),y)
	# Building the SM8250 EFI payload uses host xxd/hexdump to repackage the kernel image.
	LINUX_DEPENDENCIES += host-xxd
endif
