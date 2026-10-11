################################################################################
#
# python3-configobj
#
################################################################################

PYTHON3_CONFIGOBJ_VERSION = v5.0.9
PYTHON3_CONFIGOBJ_SITE = $(call github,DiffSK,configobj,$(PYTHON3_CONFIGOBJ_VERSION))
PYTHON3_CONFIGOBJ_SETUP_TYPE = setuptools
PYTHON3_CONFIGOBJ_LICENSE_FILES = LICENSE

$(eval $(python-package))
