################################################################################
#
# touchHLE
#
################################################################################

TOUCHHLE_VERSION = v0.2.3
TOUCHHLE_SITE = https://github.com/touchHLE/touchHLE.git
TOUCHHLE_SITE_METHOD = git
TOUCHHLE_GIT_SUBMODULES = YES
TOUCHHLE_LICENSE = GPLv2
TOUCHHLE_DEPENDENCIES =

$(eval $(rust-package))
