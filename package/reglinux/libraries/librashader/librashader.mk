################################################################################
#
# librashader
#
################################################################################

LIBRASHADER_VERSION = librashader-v0.6.2
LIBRASHADER_SITE = $(call github,SnowflakePowered,librashader,$(LIBRASHADER_VERSION))
LIBRASHADER_LICENSE = GPLv3

$(eval $(rust-package))
