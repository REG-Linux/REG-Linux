ifeq ($(BR2_PACKAGE_SYSTEM_TARGET_MT8395),y)
	# Building the MT8395 EFI payload uses host xxd/hexdump to repackage the kernel image.
	LINUX_DEPENDENCIES += host-xxd
endif
