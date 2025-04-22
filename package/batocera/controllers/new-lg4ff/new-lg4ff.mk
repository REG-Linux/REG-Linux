################################################################################
#
# new-lg4ff
#
################################################################################
# Version: Commits on Apr 14, 2025
NEW_LG4FF_VERSION = d6c8a82892b2662d017cc301aa94e255d72e9284
NEW_LG4FF_SITE = $(call github,berarma,new-lg4ff,$(NEW_LG4FF_VERSION))

$(eval $(kernel-module))
$(eval $(generic-package))
