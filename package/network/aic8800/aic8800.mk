################################################################################
#
# aic8800
#
################################################################################
# Version: Commits on Apr 21, 2025
AIC8800_VERSION = 8b8f90587527fec5d3803908cb2545379459eaa9
AIC8800_SITE = $(call github,radxa-pkg,aic8800,$(AIC8800_VERSION))
AIC8800_LICENSE = GPL-2.0
AIC8800_LICENSE_FILES = LICENSE

AIC8800_MODULE_MAKE_OPTS = \
	AIC_WLAN_SUPPORT=m \
	USER_EXTRA_CFLAGS="-DCONFIG_$(call qstrip,$(BR2_ENDIAN))_ENDIAN \
		-Wno-error"

$(eval $(kernel-module))
$(eval $(generic-package))
