################################################################################
#
# re2c
#
################################################################################

RE2C_VERSION = 4.5.1
RE2C_SITE =  $(call github,skvadrik,re2c,$(RE2C_VERSION))
RE2C_AUTORECONF = YES

$(eval $(autotools-package))
$(eval $(host-autotools-package))
