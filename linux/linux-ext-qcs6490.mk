ifeq ($(BR2_PACKAGE_SYSTEM_TARGET_QCS6490),y)
	# Building the QCS6490 EFI payload uses host hexdump to repackage the kernel image.
	LINUX_DEPENDENCIES += host-util-linux
endif
