################################################################################
#
# new-lg4ff
#
################################################################################
# Version: Commits on Dec 27, 2024
NEW_LG4FF_VERSION = v0.4.1
NEW_LG4FF_SITE = $(call github,berarma,new-lg4ff,$(NEW_LG4FF_VERSION))

$(eval $(kernel-module))
$(eval $(generic-package))
