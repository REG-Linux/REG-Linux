################################################################################
#
# itstool
#
################################################################################
ITSTOOL_VERSION = 2.0.7
ITSTOOL_SITE = $(call github,itstool,itstool,$(ITSTOOL_VERSION))
ITSTOOL_INSTALL_STAGING = YES
ITSTOOL_AUTORECONF = YES

ITSTOOL_DEPENDENCIES = python3 python-lxml
ITSTOOL_CONF_OPTS =
$(eval $(autotools-package))

HOST_ITSTOOL_CONF_OPTS =
HOST_ITSTOOL_DEPENDENCIES = host-python3 host-python-lxml
$(eval $(host-autotools-package))
