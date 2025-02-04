################################################################################
#
# touchHLE
#
################################################################################

GOPHER64_VERSION = v1.0.1
GOPHER64_SITE = $(call github,gopher64,gopher64,$(GOPHER64_VERSION))
GOPHER64_LICENSE = GPLv2
GOPHER64_DEPENDENCIES =

$(eval $(rust-package))
